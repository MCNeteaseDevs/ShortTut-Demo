# -*- coding: utf-8 -*-
#
import mod.server.extraServerApi as serverApi
import config
import random


class GeneralServer(serverApi.GetServerSystemCls()):
    def __init__(self, namespace, name):
        super(GeneralServer, self).__init__(namespace, name)
        self.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(),
                            'ServerPlayerTryDestroyBlockEvent',
                            self, self.OnTryDestroy)

    def OnTryDestroy(self, args):
        # 这里把minecraft:glass当作是幸运方块
        pos = (args["x"], args["y"], args["z"])
        identifier = args["fullName"]
        playerId = args["playerId"]
        dim = args["dimensionId"]
        if identifier != 'minecraft:glass':
            return
        # 发布一个事件，让别的系统去接管
        data = {
            "pos": pos,
            "playerId": playerId,
            "dim": dim
        }
        self.BroadcastEvent("LuckyBlockDestroyEvent", data)

    def Destroy(self):
        self.UnListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(),
                              'ServerPlayerTryDestroyBlockEvent',
                              self, self.OnTryDestroy)


class EffectServer(serverApi.GetServerSystemCls()):
    def __init__(self, namespace, name):
        super(EffectServer, self).__init__(namespace, name)
        self.ListenForEvent(config.mod_name, config.server_system_name,
                            'LuckyBlockDestroyEvent',
                            self, self.OnTryDestroyLuckyBlock)

    def OnTryDestroyLuckyBlock(self, args):
        pos = args["pos"]
        playerId = args["playerId"]
        dim = args["dim"]
        randomNum = random.randint(1, 2)
        blockInfoComp = serverApi.GetEngineCompFactory().CreateBlockInfo(serverApi.GetLevelId())
        explosionComp = serverApi.GetEngineCompFactory().CreateExplosion(serverApi.GetLevelId())
        if randomNum == 1:  # 天降铁砧
            newPos = (pos[0], pos[1] + 10, pos[2])
            blockDict = {
                "name": "minecraft:anvil",
                "aux": 0
            }
            blockInfoComp.SetBlockNew(newPos, blockDict, 0, dim)
        elif randomNum == 2:  # 产生爆炸
            explosionComp.CreateExplosion(pos, 5, True, True, playerId, playerId)

    def Destroy(self):
        self.UnListenForEvent(config.mod_name, config.server_system_name,
                              'LuckyBlockDestroyEvent',
                              self, self.OnTryDestroyLuckyBlock)
