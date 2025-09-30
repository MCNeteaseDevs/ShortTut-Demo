# -*- coding: utf-8 -*-

import mod.server.extraServerApi as serverApi
from mod.common.minecraftEnum import ActorDamageCause, ItemPosType

import demoSweepingScript.sweepingConst as sweepingConst
from mod_log import logger

ServerSystem = serverApi.GetServerSystemCls()


class SweepingServerSystem(ServerSystem):
    """
    该mod的服务端类
    """

    mobFilter = {'test': 'is_family', 'subject': 'other', 'value': 'mob'}

    def __init__(self, namespace, systemName):
        ServerSystem.__init__(self, namespace, systemName)
        self.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), "DamageEvent", self, self.OnDamage)
        self.sweepingPlayers = set()  # 正在触发横扫之刃的玩家列表

    def OnDamage(self, args):
        damage = args["damage"]
        if damage <= 0.0:
            return
        srcId = args["srcId"]
        if srcId in self.sweepingPlayers:
            # 防止死循环
            return
        entityId = args["entityId"]
        cause = args["cause"]
        if cause != ActorDamageCause.EntityAttack:
            return
        if srcId not in serverApi.GetPlayerList():
            return
        itemComp = serverApi.GetEngineCompFactory().CreateItem(srcId)
        itemDict = itemComp.GetEntityItem(ItemPosType.CARRIED)
        if not itemDict:
            return
        itemBasicInfo = itemComp.GetItemBasicInfo(itemDict["newItemName"], itemDict["newAuxValue"])
        if not itemBasicInfo:
            return
        if itemBasicInfo["itemType"] != "sword":
            return
        modEnchant = itemDict["modEnchantData"]
        level = self._GetEnchantLevel(modEnchant, "demo:sweeping") * 1.0
        if not level:
            # 没有附魔
            return
        entitiesNearby = serverApi.GetEngineCompFactory().CreateGame(entityId).GetEntitiesAround(entityId, 1, self.mobFilter)
        if entityId in entitiesNearby:
            entitiesNearby.remove(entityId)  # 删除被攻击的
        if srcId in self.sweepingPlayers:
            entitiesNearby.remove(srcId)  # 删除攻击者
        if not entitiesNearby:
            return
        finalDamage = int(1 + damage * (level / (level + 1.0)))
        self.sweepingPlayers.add(srcId)
        for entity in entitiesNearby:
            serverApi.GetEngineCompFactory().CreateHurt(entity).Hurt(finalDamage, ActorDamageCause.EntityAttack, srcId)
        self.sweepingPlayers.discard(srcId)

    def _GetEnchantLevel(self, enchantList, key):
        for enchant in enchantList:
            if enchant[0] == key:
                return enchant[1]
        return 0
