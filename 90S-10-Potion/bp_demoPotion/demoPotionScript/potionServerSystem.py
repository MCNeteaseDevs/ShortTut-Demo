# -*- coding: utf-8 -*-

import mod.server.extraServerApi as serverApi
import demoPotionScript.potionConst as potionConst
from mod_log import logger

ServerSystem = serverApi.GetServerSystemCls()
CompFactory = serverApi.GetEngineCompFactory()


def OnLingeringCloud(args):
    # 引擎按函数名找回回调。写成类方法时，DeleteEntityAOI 会报 can not find func。
    system = serverApi.GetSystem(potionConst.ModName, potionConst.ServerSystemName)
    if not system:
        return
    system.OnCloud(args)


class PotionServerSystem(ServerSystem):
    """
    该mod的服务端类
    右键丢出药水瓶子，落地生成滞留云，到时间后删除。
    """

    def __init__(self, namespace, systemName):
        ServerSystem.__init__(self, namespace, systemName)
        self.mDimensionId = None
        self.mHasCloud = False
        self.mProjectiles = {}
        self.mThrowLock = {}
        self.mRebuilding = False
        self.mExpireTimer = None
        self.mGeneration = 0
        self.mDimensionComp = None
        self.mGameComp = None
        self.mProjectileComp = None
        self.ListenForEvent(
            serverApi.GetEngineNamespace(),
            serverApi.GetEngineSystemName(),
            potionConst.AddServerPlayerEvent,
            self,
            self.OnAddPlayer
        )
        self.ListenForEvent(
            serverApi.GetEngineNamespace(),
            serverApi.GetEngineSystemName(),
            potionConst.ServerItemTryUseEvent,
            self,
            self.OnItemTryUse
        )
        self.ListenForEvent(
            serverApi.GetEngineNamespace(),
            serverApi.GetEngineSystemName(),
            potionConst.ServerItemUseOnEvent,
            self,
            self.OnItemUseOn
        )
        self.ListenForEvent(
            serverApi.GetEngineNamespace(),
            serverApi.GetEngineSystemName(),
            potionConst.ProjectileDoHitEffectEvent,
            self,
            self.OnProjectileHit
        )

    def Destroy(self):
        engineNs = serverApi.GetEngineNamespace()
        engineSys = serverApi.GetEngineSystemName()
        self.UnListenForEvent(engineNs, engineSys, potionConst.AddServerPlayerEvent, self, self.OnAddPlayer)
        self.UnListenForEvent(engineNs, engineSys, potionConst.ServerItemTryUseEvent, self, self.OnItemTryUse)
        self.UnListenForEvent(engineNs, engineSys, potionConst.ServerItemUseOnEvent, self, self.OnItemUseOn)
        self.UnListenForEvent(engineNs, engineSys, potionConst.ProjectileDoHitEffectEvent, self, self.OnProjectileHit)
        self._CancelExpire()
        self.mRebuilding = True
        self._DeleteCloud()

    def OnAddPlayer(self, args):
        playerId = args.get("id")
        if not playerId:
            return
        itemComp = CompFactory.CreateItem(playerId)
        itemComp.SpawnItemToPlayerCarried({
            "newItemName": potionConst.ITEM_NAME,
            "newAuxValue": 0,
            "count": 1,
        }, playerId)

    def OnItemTryUse(self, args):
        playerId = args.get("playerId")
        if not self._IsPotionItem(args.get("itemDict")):
            return
        args["cancel"] = True
        self._ThrowPotion(playerId)

    def OnItemUseOn(self, args):
        playerId = args.get("entityId")
        if not self._IsPotionItem(args.get("itemDict")):
            return
        args["ret"] = True
        self._ThrowPotion(playerId)

    def OnProjectileHit(self, args):
        projId = args.get("id")
        if projId not in self.mProjectiles:
            return
        args["cancel"] = True
        playerId = self.mProjectiles.pop(projId)
        self.DestroyEntity(projId)
        if args.get("hitTargetType") != "BLOCK":
            return
        if args.get("x") is None or args.get("y") is None or args.get("z") is None:
            return
        srcId = args.get("srcId") or playerId
        dimensionId = CompFactory.CreateDimension(srcId).GetEntityDimensionId()
        if dimensionId is None:
            return
        self._PlaceCloud(args.get("x"), args.get("y"), args.get("z"), dimensionId)

    def _IsPotionItem(self, itemDict):
        if not itemDict:
            return False
        itemName = itemDict.get("newItemName") or itemDict.get("itemName")
        return itemName == potionConst.ITEM_NAME

    def _ThrowPotion(self, playerId):
        if not playerId or self.mThrowLock.get(playerId):
            return
        foot = CompFactory.CreatePos(playerId).GetFootPos()
        rot = CompFactory.CreateRot(playerId).GetRot()
        if not foot or not rot:
            return
        direction = serverApi.GetDirFromRot(rot)
        if not direction:
            return
        self.mThrowLock[playerId] = True
        self._GameComp().AddTimer(0.2, self._UnlockThrow, playerId)
        spawnPos = (
            foot[0] + direction[0] * potionConst.THROW_SPAWN_FORWARD,
            foot[1] + potionConst.THROW_SPAWN_UP,
            foot[2] + direction[2] * potionConst.THROW_SPAWN_FORWARD,
        )
        projId = self._ProjectileComp().CreateProjectileEntity(playerId, potionConst.PROJECTILE_NAME, {
            "position": spawnPos,
            "direction": direction,
            "power": potionConst.THROW_POWER,
            "gravity": potionConst.THROW_GRAVITY,
            "damage": 0,
            "isDamageOwner": False,
        })
        if not projId or projId == "-1":
            logger.info("%s CreateProjectileEntity failed", potionConst.ServerSystemName)
            return
        self.mProjectiles[projId] = playerId
        logger.info("%s throw potion %s", potionConst.ServerSystemName, projId)

    def _UnlockThrow(self, playerId):
        if playerId in self.mThrowLock:
            del self.mThrowLock[playerId]

    def _PlaceCloud(self, x, y, z, dimensionId):
        oldDimensionId = self.mDimensionId

        self._CancelExpire()
        self.mRebuilding = True
        self._DeleteCloud()
        self.mRebuilding = False
        if oldDimensionId is not None and oldDimensionId != dimensionId:
            self._NotifyClearDimension(oldDimensionId)

        self.mDimensionId = dimensionId
        aabb = (
            x - potionConst.HALF_XZ,
            y - potionConst.FOOT_PAD,
            z - potionConst.HALF_XZ,
            x + potionConst.HALF_XZ,
            y + potionConst.HEIGHT,
            z + potionConst.HALF_XZ,
        )
        ok = self._DimensionComp().CreateEntityAOI(dimensionId, potionConst.AOI_NAME, aabb, OnLingeringCloud)
        if not ok:
            logger.info("%s CreateEntityAOI failed", potionConst.ServerSystemName)
            self.mDimensionId = None
            self.mHasCloud = False
            self._NotifyClearDimension(dimensionId)
            return
        self.mHasCloud = True

        self._ScheduleExpire()
        self._NotifyShow(dimensionId, x, y, z)
        logger.info(
            "%s place cloud dim=%s pos=(%s,%s,%s)",
            potionConst.ServerSystemName,
            dimensionId,
            x,
            y,
            z
        )

    def OnCloud(self, args):
        # 删旧区域时可能连带一次离开回调，重建过程中忽略
        if self.mRebuilding:
            return
        if args.get("identifier") != potionConst.PLAYER_IDENTIFIER:
            return
        if "isEnter" not in args:
            return
        entityId = args.get("entityId")
        if not entityId:
            return

        if args.get("isEnter"):
            self._ApplyEnter(entityId)
        logger.info(
            "%s cloud isEnter=%s entity=%s",
            potionConst.ServerSystemName,
            args.get("isEnter"),
            entityId
        )


    def _ApplyEnter(self, entityId):
        effectComp = CompFactory.CreateEffect(entityId)
        for effectName, duration, amplifier, showParticles in potionConst.EFFECTS:
            effectComp.AddEffectToEntity(effectName, duration, amplifier, showParticles)

    def _DeleteCloud(self):
        if not self.mHasCloud or self.mDimensionId is None:
            return
        dimensionId = self.mDimensionId
        self.mHasCloud = False
        self._DimensionComp().DeleteEntityAOI(dimensionId, potionConst.AOI_NAME)

    def _ScheduleExpire(self):
        self.mGeneration += 1
        generation = self.mGeneration
        self.mExpireTimer = self._GameComp().AddTimer(
            potionConst.CLOUD_SECONDS,
            self._OnCloudExpire,
            generation
        )

    def _CancelExpire(self):
        if self.mExpireTimer is None:
            return
        self._GameComp().CancelTimer(self.mExpireTimer)
        self.mExpireTimer = None

    def _OnCloudExpire(self, generation):
        if generation != self.mGeneration:
            return
        self.mExpireTimer = None
        dimensionId = self.mDimensionId
        self.mRebuilding = True
        self._DeleteCloud()
        self.mRebuilding = False
        self.mDimensionId = None
        self._NotifyClearDimension(dimensionId)
        logger.info("%s cloud expired", potionConst.ServerSystemName)

    def _NotifyShow(self, dimensionId, x, y, z):
        for playerId in self._PlayersInDimension(dimensionId):
            data = self.CreateEventData()
            data["x"] = x
            data["y"] = y
            data["z"] = z
            self.NotifyToClient(playerId, potionConst.ShowCloudVisualEvent, data)

    def _NotifyClear(self, playerId):
        if not playerId:
            return
        self.NotifyToClient(playerId, potionConst.ClearCloudVisualEvent, self.CreateEventData())

    def _NotifyClearDimension(self, dimensionId):
        if dimensionId is None:
            return
        for playerId in self._PlayersInDimension(dimensionId):
            self._NotifyClear(playerId)

    def _PlayersInDimension(self, dimensionId):
        players = []
        for playerId in serverApi.GetPlayerList():
            if CompFactory.CreateDimension(playerId).GetEntityDimensionId() == dimensionId:
                players.append(playerId)
        return players

    def _DimensionComp(self):
        if self.mDimensionComp is None:
            self.mDimensionComp = CompFactory.CreateDimension(serverApi.GetLevelId())
        return self.mDimensionComp

    def _GameComp(self):
        if self.mGameComp is None:
            self.mGameComp = CompFactory.CreateGame(serverApi.GetLevelId())
        return self.mGameComp

    def _ProjectileComp(self):
        if self.mProjectileComp is None:
            self.mProjectileComp = CompFactory.CreateProjectile(serverApi.GetLevelId())
        return self.mProjectileComp
