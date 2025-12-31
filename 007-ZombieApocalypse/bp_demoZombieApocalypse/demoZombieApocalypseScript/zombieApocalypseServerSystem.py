# -*- coding: utf-8 -*-

import mod.server.extraServerApi as serverApi
from mod.common.minecraftEnum import EntityType, AttrType

import demoZombieApocalypseScript.zombieApocalypseConst as zombieApocalypseConst
from mod_log import logger

from demoZombieApocalypseScript.multiplier_util import hp_multiplier, atk_multiplier

ServerSystem = serverApi.GetServerSystemCls()


class ZombieApocalypseServerSystem(ServerSystem):
    """
    该mod的服务端类
    """

    def __init__(self, namespace, systemName):
        ServerSystem.__init__(self, namespace, systemName)
        self.tick = 0
        self.timeComp = serverApi.GetEngineCompFactory().CreateTime(serverApi.GetLevelId())
        self.day = self.getDay()
        self.commandComp = serverApi.GetEngineCompFactory().CreateCommand(serverApi.GetLevelId())
        self.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), "ServerSpawnMobEvent", self, self.onMobSpawn)
        self.ListenForEvent(zombieApocalypseConst.ModName, zombieApocalypseConst.ServerSystemName, "DayChangeEvent", self, self.OnDayChange)

    def onMobSpawn(self, args):
        entityType = args["type"]
        # 只处理所有monster的type
        if entityType & EntityType.Monster != EntityType.Monster:
            return
        entityId = args["entityId"]
        attrComp = serverApi.GetEngineCompFactory().CreateAttr(entityId)
        # 设置血量
        hpRate = hp_multiplier(self.getDay())
        hpValue = attrComp.GetAttrMaxValue(AttrType.HEALTH)
        hpValue = hpValue * hpRate
        attrComp.SetAttrMaxValue(AttrType.HEALTH, hpValue)
        attrComp.SetAttrValue(AttrType.HEALTH, hpValue)
        # 设置攻击力
        atrRate = atk_multiplier(self.getDay())
        damage_value = attrComp.GetAttrValue(AttrType.DAMAGE)
        damage_value = damage_value * atrRate
        attrComp.SetAttrMaxValue(AttrType.DAMAGE, damage_value)
        attrComp.SetAttrValue(AttrType.DAMAGE, damage_value)
        print "给怪物提升属性, entityId:", entityId, " hpRate:", hpRate, " atkRate:", atrRate, "hpValue:", hpValue, " damage_value:", damage_value

    def Update(self):
        """
        1s=30tick 每秒检测一次day是否变更

        :return:
        """
        self.tick = self.tick + 1
        if self.tick >= 30:
            self.tick = 0
            day = self.getDay()
            if self.day != day:
                self.day = day
                self.BroadcastEvent("DayChangeEvent", {"day": day})

    def OnDayChange(self, args):
        day = args["day"]
        self.commandComp.SetCommand("/playsound note.pling @a")
        self.commandComp.SetCommand("/title @a title §c难度升级")
        self.commandComp.SetCommand("/title @a subtitle 第{}天".format(day))

    def getDay(self):
        passedTime = self.timeComp.GetTime()
        # 从游戏开始经过的游戏天数
        day = passedTime / 24000
        return day
