# -*- coding: utf-8 -*-

# -------------- 说明 -------------- #
# 1. 该Mod是尚未完成的Mod, 需要用户自己去实现数据持久化及数据同步
# 2. 数据持久化： 保证实体在重新登录游戏时能够重新获取同样的方块几何体模型，因此需要对方块调色板进行维持。
# 3. 数据同步：保证联机情况下所有玩家都能够看到实体的方块几何体模型，因此在服务端下发方块调色板时，需要下发到所有客户端，并生成方块几何体并添加到对应实体当中。
# --------------------------------- #

import mod.server.extraServerApi as serverApi
from mod_log import logger
from ActorBlockGeometryScripts.modCommon import modConfig

compFactory = serverApi.GetEngineCompFactory()

class ActorBlockGeometryServer(serverApi.GetServerSystemCls()):
    def __init__(self, namespace, name):
        super(ActorBlockGeometryServer, self).__init__(namespace, name)

        self.ListenEvent()
        self.mLevelId = serverApi.GetLevelId()
        self.mCombBlockVolumeLength = 2
        self.mCombBlockVolumeWidth = 2
        self.mCombBlockVolumeHeight = 1

    # 监听引擎和服务端脚本的事件
    def ListenEvent(self):
        self.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(),
                            'ClientLoadAddonsFinishServerEvent',
                            self, self.PlayerFinishLoading)
        self.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), 'ServerBlockUseEvent',
                            self, self.OnUseBlock)
        self.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), 'DestroyBlockEvent',
                            self, self.OnDestoryBlock)
        self.ListenForEvent(modConfig.modName, modConfig.modClientSystem,
                            modConfig.GetBlockPaletteEvent,
                            self, self.GetBlockPaletteRequest)
        self.ListenForEvent(modConfig.modName, modConfig.modClientSystem,
                            modConfig.DestroyBlockPaletteEvent,
                            self, self.DestroyBlockPaletteRequest)
    # 取消监听引擎和服务端脚本事件
    def UnListenEvent(self):
        self.UnDefineEvent(modConfig.PlayerClickCombBlockEvent)
        self.UnDefineEvent(modConfig.PlayerDestroyCombBlockEvent)
        self.UnDefineEvent(modConfig.SendBlockPaletteEvent)
        self.UnListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(),
                              'ServerBlockUseEvent',
                              self, self.OnUseBlock)
        self.UnListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(),
                              'ClientLoadAddonsFinishServerEvent',
                              self, self.PlayerFinishLoading)
        self.UnListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), 'DestroyBlockEvent',
                              self, self.OnDestoryBlock)
        self.UnListenForEvent(modConfig.modName, modConfig.modClientSystem,
                            modConfig.DestroyBlockPaletteEvent,
                            self, self.DestroyBlockPaletteRequest)

    def PlayerFinishLoading(self, args):
        playerId = args['playerId']
        itemDict = {
            'itemName': 'actorBlockGeometryMod:custom_combBlock',
            'count': 32,
            'auxValue': 0,
            'customTips': '§c my new item !! §r'
        }
        comp = compFactory.CreateItem(playerId)
        comp.SpawnItemToPlayerInv(itemDict, playerId, 0)

    # 玩家点击组合方块
    def OnUseBlock(self, args):
        playerId = args['playerId']
        blockName = args['blockName']
        if blockName == 'actorblockgeometrymod:custom_combblock':
            eventData = self.CreateEventData()
            eventData['blockPos'] = (args['x'], args['y'], args['z'])
            self.NotifyToClient(playerId, modConfig.PlayerClickCombBlockEvent, eventData)

    # 玩家破坏组合方块
    def OnDestoryBlock(self, args):
        playerId = args['playerId']
        blockName = args['fullName']
        if blockName == 'actorblockgeometrymod:custom_combblock':
            eventData = self.CreateEventData()
            self.NotifyToClient(playerId, modConfig.PlayerDestroyCombBlockEvent, eventData)

    # 处理从客户端发来的获取方块调色板请求
    def GetBlockPaletteRequest(self, args):
        blockPos = args['blockPos']
        playerId = args['playerId']
        dimensionComp = compFactory.CreateDimension(playerId)
        dimensionId = dimensionComp.GetEntityDimensionId()
        # 获取方块调色板
        x1, y1, z1 = blockPos[0] - self.mCombBlockVolumeWidth, blockPos[1] - self.mCombBlockVolumeHeight, blockPos[2] - self.mCombBlockVolumeLength
        x2, y2, z2 = blockPos[0] + self.mCombBlockVolumeWidth, blockPos[1], blockPos[2] + self.mCombBlockVolumeLength
        blockComp = compFactory.CreateBlock(playerId)
        palette = blockComp.GetBlockPaletteBetweenPos(dimensionId, (x1, y1, z1), (x2, y2, z2))
        if palette is not None:
            logger.info("===== BlockPalette construct successfully =====")
            eventData = self.CreateEventData()
            # 创建一个实体，直到实体真正生成为止
            entityId = self.CreateEngineEntityByTypeStr('actorblockgeometrymod:entity_driver', blockPos, (0, 0), dimensionId)
            if entityId:
                # 将区域置为空气
                import mod.server.extraServerApi as serverApi
                comp = compFactory.CreateCommand(serverApi.GetLevelId())
                comp.SetCommand("/fill %s %s %s %s %s %s air" % (x1,y1,z1,x2,y2,z2))
                eventData['entityId'] = entityId
                # 序列化方块调色板数据
                eventData['palette'] = palette.SerializeBlockPalette()
                self.NotifyToClient(playerId, modConfig.SendBlockPaletteEvent, eventData)

    # 处理从客户端发来的解除方块几何体模型请求
    def DestroyBlockPaletteRequest(self, eventData):
        entityId = eventData['entityId']
        entityFootPos = eventData['blockPos']
        paletteData = eventData['palette']
        # 获取一个空白的方块调色板
        blockComp = compFactory.CreateBlock(serverApi.GetLevelId())
        blockPalette = blockComp.GetBlankBlockPalette()
        # 反序列化方块调色板数据
        blockPalette.DeserializeBlockPalette(paletteData)
        dimensionComp = compFactory.CreateDimension(entityId)
        dimensionId = dimensionComp.GetEntityDimensionId()
        # 删除实体
        if self.DestroyEntity(entityId):
            # 利用方块调色板重新设置方块
            blockComp.SetBlockByBlockPalette(blockPalette, dimensionId, entityFootPos, 0, 0)

    # 在清除该system的时候调用取消监听事件
    def Destroy(self):
        logger.info("===== ActorBlockGeometryMod Server System Destroy =====")
        self.UnListenEvent()
