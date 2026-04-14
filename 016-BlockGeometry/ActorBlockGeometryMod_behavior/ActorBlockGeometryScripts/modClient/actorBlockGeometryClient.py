# -*- coding: utf-8 -*-

# -------------- 说明 -------------- #
# 1. 该Mod是尚未完成的Mod, 需要用户自己去实现数据持久化及数据同步
# 2. 数据持久化： 保证实体在重新登录游戏时能够重新获取同样的方块几何体模型，因此需要对方块调色板进行维持。
# 3. 数据同步：保证联机情况下所有玩家都能够看到实体的方块几何体模型，因此在服务端下发方块调色板时，需要下发到所有客户端，并生成方块几何体并添加到对应实体当中。
# --------------------------------- #

import mod.client.extraClientApi as clientApi
from mod_log import logger
from ActorBlockGeometryScripts.modCommon import modConfig

compFactory = clientApi.GetEngineCompFactory()

class ActorBlockGeometryClient(clientApi.GetClientSystemCls()):
    def __init__(self, namespace, name):
        super(ActorBlockGeometryClient, self).__init__(namespace, name)

        self.ListenEvent()
        self.mBaseUINode = None
        self.mBlockPos = ()
        self.mBlockPalette = None
        self.mGeometryName = "my_block_geometry"
        self.mTimer = None
        self.mActorRenderComp = None
        self.mEntityId = None

    # 监听引擎和服务端脚本的事件
    def ListenEvent(self):
        self.ListenForEvent(clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(), 'UiInitFinished',
                            self, self.OnUIInitFinished)
        self.ListenForEvent(modConfig.modName, modConfig.modServerSystem, modConfig.PlayerClickCombBlockEvent,
                            self, self.PlayerClickCombBlock)
        self.ListenForEvent(modConfig.modName, modConfig.modServerSystem,
                            modConfig.PlayerDestroyCombBlockEvent,
                            self, self.PlayerDestroyCombBlock)
        self.ListenForEvent(modConfig.modName, modConfig.modServerSystem,
                            modConfig.SendBlockPaletteEvent,
                            self, self.OnReceiveBlockPalette)

    # 取消监听引擎和服务端脚本事件
    def UnListenEvent(self):
        self.UnDefineEvent(modConfig.GetBlockPaletteEvent)
        self.UnDefineEvent(modConfig.DestroyBlockPaletteEvent)
        self.UnListenForEvent(clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(), 'UiInitFinished',
                              self, self.OnUIInitFinished)
        self.UnListenForEvent(modConfig.modName, modConfig.modServerSystem, modConfig.PlayerClickCombBlockEvent,
                              self, self.PlayerClickCombBlock)
        self.UnListenForEvent(modConfig.modName, modConfig.modServerSystem,
                              modConfig.PlayerDestroyCombBlockEvent,
                              self, self.PlayerDestroyCombBlock)
        self.UnListenForEvent(modConfig.modName, modConfig.modServerSystem,
                            modConfig.SendBlockPaletteEvent,
                            self, self.OnReceiveBlockPalette)

    # 监听引擎初始化完成事件，在这个事件后创建UI
    def OnUIInitFinished(self, args):
        clientApi.RegisterUI(modConfig.modName, "ActorBlockGeoModUI",
                             "ActorBlockGeometryScripts.modClient.ui.MainScreen.MainScreen",
                             "ActorBlockGeoModUI.main")
        clientApi.RegisterUI(modConfig.modName, "BlockUI",
                             "ActorBlockGeometryScripts.modClient.ui.MainScreen.ButtonScreen",
                             "BlockUI.main")
        clientApi.CreateUI(modConfig.modName, "ActorBlockGeoModUI", {"isHud": 1})
        self.mBaseUINode = clientApi.GetUI(modConfig.modName, "ActorBlockGeoModUI")

    # 玩家点击组合方块，弹出或关闭组合方块UI界面
    def PlayerClickCombBlock(self, args):
        self.mBlockPos = args['blockPos']
        if self.mBaseUINode:
            self.mBaseUINode.OnOpenCloseButtonPanel()

    # 玩家破坏组合方块，关闭组合方块UI界面
    def PlayerDestroyCombBlock(self, args):
        self.mBlockPos = ()
        if self.mBaseUINode:
            self.mBaseUINode.OnCloseButtonPanel()
        self.clearData()

    # 向服务端发送组合方块事件
    def SendGetBlockPalette(self):
        if self.mBlockPalette:
            logger.info("===== You already have a block comp ! =====")
            return

        eventData = self.CreateEventData()
        eventData['blockPos'] = self.mBlockPos
        eventData['playerId'] = clientApi.GetLocalPlayerId()
        self.NotifyToServer(modConfig.GetBlockPaletteEvent, eventData)

    # 解除方块几何体模型并向服务端发送重新设置方块
    def SendDestoryBlockPalette(self):
        if self.mEntityId and self.mBlockPalette:
            actorRenderComp = compFactory.CreateActorRender(self.mEntityId)
            # 清空实体的方块几何体模型
            actorRenderComp.ClearActorBlockGeometry()
            # 发送请求
            eventData = self.CreateEventData()
            eventData['entityId'] = self.mEntityId
            # 获取位置
            posComp = clientApi.GetEngineCompFactory().CreatePos(self.mEntityId)
            entityFootPos = posComp.GetFootPos()
            eventData['blockPos'] = entityFootPos
            # 序列化方块调色板数据
            eventData['palette'] = self.mBlockPalette.SerializeBlockPalette()
            self.NotifyToServer(modConfig.DestroyBlockPaletteEvent, eventData)
            # 获取方块调色板中组合方块的位置
            localPosList = self.mBlockPalette.GetLocalPosListOfBlocks("actorblockgeometrymod:custom_combblock")

            self.clearData()
            if len(localPosList) == 1:
                # 重新获取解除方块组合后组合方块的世界坐标
                localPos = localPosList[0]
                self.mBlockPos = (entityFootPos[0]+localPos[0], entityFootPos[1]+localPos[1],entityFootPos[2]+localPos[2])
            logger.info("===== Release block comp successfully ! =====")
        else:
            logger.info("===== No block comp exists. You must have one ! =====")
            
        if self.mBaseUINode:
            self.mBaseUINode.OnCloseButtonPanel()

    # 收到从服务端获取的方块调色板
    def OnReceiveBlockPalette(self, data):
        paletteData = data['palette']
        self.mEntityId = data['entityId']
        # 获取一个空白的方块调色板
        comp = compFactory.CreateBlock(clientApi.GetLocalPlayerId())
        self.mBlockPalette = comp.GetBlankBlockPalette()
        # 反序列化方块调色板数据
        self.mBlockPalette.DeserializeBlockPalette(paletteData)
        # 合并方块组合并生成方块几何体模型
        blockGeometryComp = compFactory.CreateBlockGeometry(clientApi.GetLocalPlayerId())
        blockGeometryComp.CombineBlockPaletteToGeometry(self.mBlockPalette, self.mGeometryName)
        # 添加定时器，直到实体真正存在时才为该实体添加方块几何体模型
        gameComp = compFactory.CreateGame(clientApi.GetLevelId())
        self.mTimer = gameComp.AddRepeatedTimer(0.1, self.CheckEntityAndAddBlockGeometry, self.mEntityId)
        logger.info("===== Get block comp successfully ! =====")

    def CheckEntityAndAddBlockGeometry(self, entityId):
        gameComp = compFactory.CreateGame(clientApi.GetLevelId())
        exist = gameComp.HasEntity(entityId)
        if exist:
            gameComp.CancelTimer(self.mTimer)
            # 添加到实体中
            actorRenderComp = compFactory.CreateActorRender(entityId)
            actorRenderComp.AddActorBlockGeometry(self.mGeometryName, (-2,0,-2))

    # 清空保存的数据
    def clearData(self):
        self.mBlockPos = ()
        self.mBlockPalette = None
        self.mTimer = None

    # 在清除该system的时候调用取消监听事件
    def Destroy(self):
        logger.info("===== ActorBlockGeometryMod Client System Destroy =====")
        self.UnListenEvent()
