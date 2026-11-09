# -*- coding: utf-8 -*-

import mod.client.extraClientApi as clientApi
from mod_log import logger

import compoundBowScript.compoundBowConst as conf

ClientSystem = clientApi.GetClientSystemCls()
CompFactory = clientApi.GetEngineCompFactory()


class CompoundBowClientSystem(ClientSystem):
    """
    客户端只负责表现：
    1. 蓄力时把 FOV 慢慢拉近，松手恢复
    2. 松手时把 q.mod.compound_bow_shoot 置 1，让 attachable 播射击动画
    3. 注册动画需要的自定义 Molang 节点
    """

    def __init__(self, namespace, systemName):
        ClientSystem.__init__(self, namespace, systemName)
        self.mPlayerId = None
        self.mCamera = None
        self.mActorRender = None
        self.mQuery = None
        self.mPlayerQuery = None
        self.mInitFov = conf.DEFAULT_FOV
        self.mLastFov = None
        self.mTick = 0
        self.mDrawing = False
        self.mDrawStart = 0
        self.mShootUntil = 0

        engineNs = clientApi.GetEngineNamespace()
        engineSys = clientApi.GetEngineSystemName()
        self.ListenForEvent(engineNs, engineSys, conf.OnLocalPlayerStopLoading, self, self.OnLocalPlayerStopLoading)
        self.ListenForEvent(engineNs, engineSys, conf.ClientItemTryUseEvent, self, self.OnClientItemTryUse)
        self.ListenForEvent(engineNs, engineSys, conf.ItemReleaseUsingClientEvent, self, self.OnItemReleaseUsing)
        self.ListenForEvent(engineNs, engineSys, conf.StopUsingItemClientEvent, self, self.OnStopUsingItem)
        self.ListenForEvent(engineNs, engineSys, conf.OnCarriedNewItemChangedClientEvent, self, self.OnCarriedNewItemChanged)
        self.ListenForEvent(engineNs, engineSys, conf.OnScriptTickClient, self, self.OnScriptTickClient)

    def Destroy(self):
        engineNs = clientApi.GetEngineNamespace()
        engineSys = clientApi.GetEngineSystemName()
        self.UnListenForEvent(engineNs, engineSys, conf.OnLocalPlayerStopLoading, self, self.OnLocalPlayerStopLoading)
        self.UnListenForEvent(engineNs, engineSys, conf.ClientItemTryUseEvent, self, self.OnClientItemTryUse)
        self.UnListenForEvent(engineNs, engineSys, conf.ItemReleaseUsingClientEvent, self, self.OnItemReleaseUsing)
        self.UnListenForEvent(engineNs, engineSys, conf.StopUsingItemClientEvent, self, self.OnStopUsingItem)
        self.UnListenForEvent(engineNs, engineSys, conf.OnCarriedNewItemChangedClientEvent, self, self.OnCarriedNewItemChanged)
        self.UnListenForEvent(engineNs, engineSys, conf.OnScriptTickClient, self, self.OnScriptTickClient)
        self._ResetFov()

    def OnLocalPlayerStopLoading(self, args):
        self.mPlayerId = args.get("playerId") or clientApi.GetLocalPlayerId()
        if not self.mPlayerId:
            return
        self.mCamera = CompFactory.CreateCamera(clientApi.GetLevelId())
        fov = self.mCamera.GetFov()
        if fov:
            self.mInitFov = fov
        self.mActorRender = CompFactory.CreateActorRender(self.mPlayerId)
        self._RegisterMolang()
        self._InitArmRender()

    def _RegisterMolang(self):
        # 和 combatDrone 一样：先注册默认值，再把第一人称修正值写到玩家身上
        levelId = clientApi.GetLevelId()
        defaults = (
            (conf.MOLANG_BREATHE, 1.0),
            (conf.MOLANG_AIM, 0.0),
            (conf.MOLANG_SHOOT, 0.0),
            (conf.MOLANG_FIX_X, 0.0),
            (conf.MOLANG_FIX_Z, 0.0),
            (conf.MOLANG_SPEED, 1.0),
        ) + conf.DEPLOY_DEFAULTS
        self.mQuery = CompFactory.CreateQueryVariable(levelId)
        for name, value in defaults:
            self.mQuery.Register(name, value)

        self.mPlayerQuery = CompFactory.CreateQueryVariable(self.mPlayerId)
        for name, value in defaults:
            self.mPlayerQuery.Set(name, value)

        width, height = CompFactory.CreateGame(levelId).GetScreenSize()
        rate = width / float(height) if height else conf.FIX_OFFSET_MAX_RATE
        fixX = conf.FIX_OFFSET_FACTOR * (min(rate, conf.FIX_OFFSET_MAX_RATE) - conf.FIX_OFFSET_MAX_RATE)
        modelStyle = self.mActorRender.GetModelStyle() if self.mActorRender else "normal"
        fixZ = conf.SLIM_FIX_OFFSET_Z if modelStyle == "slim" else 0.0
        self.mPlayerQuery.Set(conf.MOLANG_FIX_X, fixX)
        self.mPlayerQuery.Set(conf.MOLANG_FIX_Z, fixZ)

    def _InitArmRender(self):
        # 武器是 attachable，手是挂到玩家身上的 arm geometry；
        # 把 1st/3rd 动画同时加到玩家，玩家真手臂才会和弓一起动。
        if not self.mActorRender:
            return
        actorComp = self.mActorRender
        actorComp.AddPlayerGeometry(conf.ARM_GEOMETRY_KEY, "geometry.compound_bow_arm")
        actorComp.AddPlayerRenderController(
            conf.ARM_RENDER_CONTROLLER,
            "v.is_first_person && " + conf.BOW_ITEM_CONDITION
        )
        for animKey, animName in conf.ARM_ANIM_MAP:
            actorComp.AddPlayerAnimation(animKey, animName)
        actorComp.AddPlayerAnimationController(conf.ARM_CONTROLLER_KEY, conf.ARM_CONTROLLER_NAME)
        actorComp.AddPlayerScriptAnimate(conf.ARM_CONTROLLER_KEY, conf.BOW_ITEM_CONDITION, True)
        actorComp.RebuildPlayerRender()
        logger.info("%s arm render init", conf.ClientSystemName)

    def OnClientItemTryUse(self, args):
        itemDict = args.get("itemDict") or {}
        if not self._IsItem(itemDict, conf.BOW_NAME):
            return
        if self.mDrawing:
            return
        if not self.mCamera:
            return
        fov = self.mCamera.GetFov()
        if fov:
            self.mInitFov = fov
        self.mDrawing = True
        self.mDrawStart = self.mTick
        self.mLastFov = None
        self._SetAim(True)

    def OnItemReleaseUsing(self, args):
        itemDict = args.get("itemDict") or {}
        if not self._IsItem(itemDict, conf.BOW_NAME):
            return
        wasDrawing = self.mDrawing
        held = self.mTick - self.mDrawStart
        self._ResetFov()
        self._SetAim(False)
        # 和服务端 MIN_CHARGE 对齐：轻点一下不播射击动画
        if wasDrawing and held >= conf.DRAW_TICKS * conf.MIN_CHARGE:
            self._PlayShootAnim()

    def OnStopUsingItem(self, args):
        itemDict = args.get("itemDict") or {}
        if not self._IsItem(itemDict, conf.BOW_NAME):
            return
        self._ResetFov()
        self._SetAim(False)

    def OnCarriedNewItemChanged(self, args):
        # 蓄力途中切走武器时，避免 FOV 卡在拉近状态
        itemDict = args.get("itemDict") or {}
        if self.mDrawing and not self._IsItem(itemDict, conf.BOW_NAME):
            self._ResetFov()
            self._SetAim(False)

    def OnScriptTickClient(self):
        self.mTick += 1
        if self.mDrawing:
            self._ApplyFov()
        if self.mShootUntil and self.mTick >= self.mShootUntil:
            self.mShootUntil = 0
            if self.mPlayerQuery:
                self.mPlayerQuery.Set(conf.MOLANG_SHOOT, 0.0)

    def _ApplyFov(self):
        if not self.mCamera:
            return
        progress = min(1.0, (self.mTick - self.mDrawStart) / float(conf.DRAW_TICKS))
        fov = max(conf.FOV_MIN, self.mInitFov - conf.FOV_ZOOM * progress)
        if fov != self.mLastFov:
            self.mCamera.SetFov(fov)
            self.mLastFov = fov

    def _ResetFov(self):
        self.mDrawing = False
        self.mLastFov = None
        if self.mCamera:
            self.mCamera.SetFov(self.mInitFov)

    def _PlayShootAnim(self):
        if not self.mPlayerQuery:
            return
        self.mPlayerQuery.Set(conf.MOLANG_SHOOT, 1.0)
        self.mShootUntil = self.mTick + conf.SHOOT_ANIM_TICKS
        logger.info("%s shoot anim", conf.ClientSystemName)

    def _SetAim(self, aiming):
        if not self.mPlayerQuery:
            return
        self.mPlayerQuery.Set(conf.MOLANG_AIM, 1.0 if aiming else 0.0)

    def _IsItem(self, itemDict, itemName):
        if not itemDict:
            return False
        name = itemDict.get("newItemName") or itemDict.get("itemName")
        return name == itemName
