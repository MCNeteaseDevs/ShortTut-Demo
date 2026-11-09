# -*- coding: utf-8 -*-

import mod.server.extraServerApi as serverApi
from mod.common.minecraftEnum import ItemPosType
from mod_log import logger

import compoundBowScript.compoundBowConst as conf

ServerSystem = serverApi.GetServerSystemCls()
CompFactory = serverApi.GetEngineCompFactory()


class CompoundBowServerSystem(ServerSystem):
    """
    自定义远程武器的服务端逻辑：
    1. 进世界发一把复合弓和一组箭
    2. 右键抬起时计算蓄力比例
    3. 扣一支箭，按蓄力比例生成自定义箭矢
    """

    def __init__(self, namespace, systemName):
        ServerSystem.__init__(self, namespace, systemName)
        self.mProjectileComp = None
        engineNs = serverApi.GetEngineNamespace()
        engineSys = serverApi.GetEngineSystemName()
        self.ListenForEvent(engineNs, engineSys, conf.AddServerPlayerEvent, self, self.OnAddPlayer)
        self.ListenForEvent(engineNs, engineSys, conf.ItemReleaseUsingServerEvent, self, self.OnItemReleaseUsing)

    def Destroy(self):
        engineNs = serverApi.GetEngineNamespace()
        engineSys = serverApi.GetEngineSystemName()
        self.UnListenForEvent(engineNs, engineSys, conf.AddServerPlayerEvent, self, self.OnAddPlayer)
        self.UnListenForEvent(engineNs, engineSys, conf.ItemReleaseUsingServerEvent, self, self.OnItemReleaseUsing)

    def OnAddPlayer(self, args):
        # 注意：AddServerPlayerEvent 的玩家 id 参数叫 id，不是 playerId
        playerId = args.get("id")
        if not playerId:
            return
        itemComp = CompFactory.CreateItem(playerId)
        itemComp.SpawnItemToPlayerInv({
            "newItemName": conf.BOW_NAME,
            "newAuxValue": 0,
            "count": 1,
        }, playerId, conf.BOW_SLOT)
        itemComp.SpawnItemToPlayerInv({
            "newItemName": conf.AMMO_NAME,
            "newAuxValue": 0,
            "count": conf.AMMO_COUNT,
        }, playerId, conf.AMMO_SLOT)

    def OnItemReleaseUsing(self, args):
        playerId = args.get("playerId")
        itemDict = args.get("itemDict") or {}
        if not playerId or not self._IsItem(itemDict, conf.BOW_NAME):
            return

        ratio = self._ChargeRatio(args)
        if ratio < conf.MIN_CHARGE:
            self._Tip(playerId, "蓄力不足，再拉久一点")
            return
        if not self._ConsumeAmmo(playerId):
            self._Tip(playerId, "没有箭了")
            return

        self._Shoot(playerId, ratio)
        logger.info("%s shoot ratio=%.2f", conf.ServerSystemName, ratio)

    def _ChargeRatio(self, args):
        # durationLeft 是剩余蓄力时间，maxUseDuration 是总时长，两者相减就是已经拉了多久
        maxUse = args.get("maxUseDuration") or 0
        durationLeft = args.get("durationLeft")
        if maxUse <= 0 or durationLeft is None or durationLeft < 0:
            # 没有配置 minecraft:use_duration 时 durationLeft 会是负数，这里给一个中间值兜底
            return 0.5
        held = max(0.0, float(maxUse) - float(durationLeft))
        fullTicks = conf.TICKS_PER_SECOND * conf.FULL_CHARGE_SECONDS
        return min(1.0, held / fullTicks)

    def _ConsumeAmmo(self, playerId):
        itemComp = CompFactory.CreateItem(playerId)
        items = itemComp.GetPlayerAllItems(ItemPosType.INVENTORY, True)
        if not items:
            return False
        for slot, item in enumerate(items):
            if not item:
                continue
            if not self._IsItem(item, conf.AMMO_NAME):
                continue
            count = item.get("count", 0)
            if count <= 0:
                continue
            # 数量减一，减到 0 就是清掉这一格
            itemComp.SetInvItemNum(slot, count - 1)
            return True
        return False

    def _Shoot(self, playerId, ratio):
        footPos = CompFactory.CreatePos(playerId).GetFootPos()
        rot = CompFactory.CreateRot(playerId).GetRot()
        if not footPos or not rot:
            return
        direction = serverApi.GetDirFromRot(rot)
        if not direction:
            return

        power = conf.MIN_POWER + (conf.MAX_POWER - conf.MIN_POWER) * ratio
        damage = conf.MIN_DAMAGE + (conf.MAX_DAMAGE - conf.MIN_DAMAGE) * ratio
        spawnPos = (
            footPos[0] + direction[0] * conf.SPAWN_FORWARD,
            footPos[1] + conf.SPAWN_UP,
            footPos[2] + direction[2] * conf.SPAWN_FORWARD,
        )
        param = {
            "position": spawnPos,
            "direction": direction,
            "power": power,
            "gravity": conf.GRAVITY,
            "damage": damage,
            "isDamageOwner": False,
        }
        projectileId = self._ProjectileComp().CreateProjectileEntity(
            playerId,
            conf.ARROW_ENTITY,
            param
        )
        if not projectileId or projectileId == "-1":
            logger.info("%s CreateProjectileEntity failed", conf.ServerSystemName)
            return
        logger.info("%s projectile=%s power=%.2f damage=%.2f",
                    conf.ServerSystemName, projectileId, power, damage)

    def _ProjectileComp(self):
        if self.mProjectileComp is None:
            self.mProjectileComp = CompFactory.CreateProjectile(serverApi.GetLevelId())
        return self.mProjectileComp

    def _Tip(self, playerId, message):
        CompFactory.CreateGame(playerId).SetOneTipMessage(playerId, message)

    def _IsItem(self, itemDict, itemName):
        if not itemDict:
            return False
        name = itemDict.get("newItemName") or itemDict.get("itemName")
        return name == itemName
