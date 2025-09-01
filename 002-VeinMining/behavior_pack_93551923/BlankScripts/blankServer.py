# -*- coding: utf-8 -*-
#
import mod.server.extraServerApi as serverApi


class BlankServer(serverApi.GetServerSystemCls()):
    def __init__(self, namespace, name):
        super(BlankServer, self).__init__(namespace, name)
        self.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(),
                            "ServerPlayerTryDestroyBlockEvent", self, self.OnTryDestroy)  # 监听玩家破坏方块事件
        self.searchingPlayers = set()  # 用来存储正在连锁挖掘的玩家

    def Destroy(self):
        self.UnListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(),
                              "ServerPlayerTryDestroyBlockEvent", self, self.OnTryDestroy)

    def OnTryDestroy(self, args):
        pos = (args["x"], args["y"], args["z"])
        dim = args["dimensionId"]
        playerId = args["playerId"]
        blockIdentifier = args["fullName"]  # 被破坏的方块类型
        if playerId in self.searchingPlayers:
            # 防止死循环
            return
        self.searchingPlayers.add(playerId)  # 将玩家加入连锁状态，防止死循环
        blocks = self.SearchBlocks(blockIdentifier, pos, dim)  # 搜索-1到1范围内的方块
        playerBlockInfoComp = serverApi.GetEngineCompFactory().CreateBlockInfo(playerId)
        for newPos in blocks:
            playerBlockInfoComp.PlayerDestoryBlock(newPos)  # 破坏找到的方块
        self.searchingPlayers.discard(playerId)  # 让玩家退出连锁状态

    def SearchBlocks(self, identifier, pos, dim, range=1):
        # 从-range到range搜索周围的方块
        blockInfoComp = serverApi.GetEngineCompFactory().CreateBlockInfo(serverApi.GetLevelId())
        offset = xrange(-range, range + 1)  # 这里为[-1,0,1]
        result = []
        for y in offset:
            # 从y=-1到y=1遍历
            for x in offset:
                # 从x=-1到x=1遍历
                for z in offset:
                    # 从z=-1到z=1遍历
                    newPos = (pos[0] + x, pos[1] + y, pos[2] + z)
                    # 新的坐标
                    blockInfo = blockInfoComp.GetBlockNew(newPos, dim)
                    blockName = blockInfo["name"]
                    if blockName == identifier:
                        # 如果方块一样，就加入搜索结果
                        result.append(newPos)
        return result
