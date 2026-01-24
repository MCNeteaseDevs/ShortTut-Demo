# -*- coding: utf-8 -*-

import mod.server.extraServerApi as serverApi
from mod.common.minecraftEnum import AttrType

import demoHealthRegenScript.healthRegenConst as healthRegenConst
from mod_log import logger

ServerSystem = serverApi.GetServerSystemCls()


class HealthRegenServerSystem(ServerSystem):
    """
    该mod的服务端类
    """

    def __init__(self, namespace, systemName):
        ServerSystem.__init__(self, namespace, systemName)
        self.tickCache = {}
        self.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), "DelServerPlayerEvent", self, self.OnDelPlayer)

    def OnDelPlayer(self, args):
        playerId = args.get("playerId")
        cache = self.tickCache.get(playerId)
        if cache:
            # 还原
            playerComp = serverApi.GetEngineCompFactory().CreatePlayer(playerId)
            del self.tickCache[playerId]
            playerComp.SetPlayerHealthTick(cache)

    def Update(self):
        for playerId in serverApi.GetPlayerList():
            attrComp = serverApi.GetEngineCompFactory().CreateAttr(playerId)
            playerComp = serverApi.GetEngineCompFactory().CreatePlayer(playerId)
            cache = self.tickCache.get(playerId)
            if attrComp.GetAttrValue(AttrType.HUNGER) == attrComp.GetAttrMaxValue(AttrType.HUNGER) and attrComp.GetAttrValue(AttrType.SATURATION) > 0.0 and not cache:
                self.tickCache[playerId] = playerComp.GetPlayerHealthTick()
                playerComp.SetPlayerHealthTick(10)
            elif cache:
                del self.tickCache[playerId]
                playerComp.SetPlayerHealthTick(cache)
