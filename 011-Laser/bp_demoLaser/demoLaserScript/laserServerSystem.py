# -*- coding: utf-8 -*-

import mod.server.extraServerApi as serverApi
import demoLaserScript.laserConst as laserConst
from mod_log import logger

ServerSystem = serverApi.GetServerSystemCls()


class LaserServerSystem(ServerSystem):
    """
    该mod的服务端类
    """

    def __init__(self, namespace, systemName):
        ServerSystem.__init__(self, namespace, systemName)
        print "LaserServerSystem init"
        self.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), "ServerItemTryUseEvent", self, self.OnUse)
        self.gameComp = serverApi.GetEngineCompFactory().CreateGame(serverApi.GetLevelId())

    def OnUse(self, args):
        playerId = args["playerId"]
        itemDict = args["itemDict"]
        if not itemDict:
            return
        if itemDict["newItemName"] != "minecraft:stick":
            return
        self.DoLaser(playerId)

    def DoLaser(self, playerId):
        fromPos = serverApi.GetEngineCompFactory().CreatePos(playerId).GetPos()
        fromRot = serverApi.GetEngineCompFactory().CreateRot(playerId).GetRot()
        dirVec = serverApi.GetDirFromRot(fromRot)
        dim = serverApi.GetEngineCompFactory().CreateDimension(playerId).GetEntityDimensionId()
        blocks = serverApi.getEntitiesOrBlockFromRay(dim, fromPos, dirVec, 50, False, serverApi.GetMinecraftEnum().RayFilterType.OnlyBlocks)
        if not blocks:
            return
        hitInfo = blocks[0]
        toPos = hitInfo["hitPos"]
        print "ray hit at:", toPos
        for playerId in serverApi.GetPlayerList():
            if serverApi.GetEngineCompFactory().CreateDimension(playerId).GetEntityDimensionId() != dim:
                continue
            self.NotifyToClient(playerId, "PlayParticleEffectClientEvent", {
                "from": fromPos,
                "dim": dim,
                "to": toPos,
            })

        def laterExplode():
            serverApi.GetEngineCompFactory().CreateExplosion(serverApi.GetLevelId()).CreateExplosion(toPos, 10, True, True, playerId, playerId)

        self.gameComp.AddTimer(0.25, laterExplode)
