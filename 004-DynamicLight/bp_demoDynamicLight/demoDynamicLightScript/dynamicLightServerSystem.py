# -*- coding: utf-8 -*-
import mod.server.extraServerApi as serverApi
from math import floor

ServerSystem = serverApi.GetServerSystemCls()


class DynamicLightServerSystem(ServerSystem):
    LIGHT_MAPPING = {
        "minecraft:torch": 15,
        "minecraft:redstone_torch": 7,
        "minecraft:glowstone": 15,
        "minecraft:sea_lantern": 15,
        "minecraft:jack_o_lantern": 15,
        "minecraft:lantern": 15,
        "minecraft:soul_lantern": 10,
        "minecraft:campfire": 15,
        "minecraft:soul_campfire": 10,
    }
    DIM = 0
    CHECK_INTERVAL = 2  # 检查间隔（tick）

    def __init__(self, namespace, systemName):
        ServerSystem.__init__(self, namespace, systemName)
        self.blockInfoComp = serverApi.GetEngineCompFactory().CreateBlockInfo(serverApi.GetLevelId())
        self.gameComp = serverApi.GetEngineCompFactory().CreateGame(serverApi.GetLevelId())
        # 性能优化：减少检查频率
        self.tickCounter = 0
        self.playerPos = {}
        self.playerLightLevel = {}
        self.playerLightBlockPos = {}
        self.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), "OnCarriedNewItemChangedServerEvent", self, self.OnCarryNewItem)
        self.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), "DelServerPlayerEvent", self, self.OnQuit)

    def _RemoveLightBlock(self, playerId):
        """移除玩家的光源方块"""
        pos = self.playerLightBlockPos.get(playerId)
        if not pos:
            return False

        blockDict = self.blockInfoComp.GetBlockNew(pos, self.DIM)
        if not blockDict:
            return False

        # 只移除我们创建的光源方块
        if blockDict["name"] == "minecraft:light_block":
            self.blockInfoComp.SetBlockNew(pos, {"name": "minecraft:air"}, dimensionId=self.DIM)
            del self.playerLightBlockPos[playerId]
            return True

        return False

    def _SetLightBlock(self, playerId, newPos):
        """在新位置设置光源方块"""
        lightLevel = self.playerLightLevel.get(playerId)
        if not lightLevel:
            return False

        # 检查新位置是否为空气
        blockDict = self.blockInfoComp.GetBlockNew(newPos, self.DIM)
        if not blockDict or blockDict["name"] != "minecraft:air":
            return False

        # 设置光源方块
        lightBlockName = "minecraft:light_block"
        success = self.blockInfoComp.SetBlockNew(newPos, {"name": lightBlockName, "aux": lightLevel}, dimensionId=self.DIM)

        if success:
            self.playerLightBlockPos[playerId] = newPos
            return True

        return False

    def _UpdatePlayerLight(self, playerId):
        """更新玩家的光源"""
        print("Updating light for player:", playerId)
        # 先移除旧的光源
        self._RemoveLightBlock(playerId)

        posComp = serverApi.GetEngineCompFactory().CreatePos(playerId)
        pos = posComp.GetPos()
        # 转换为整数坐标
        intPos = tuple([int(floor(x)) for x in pos])

        # 在新位置设置光源
        if self.playerLightLevel.get(playerId):
            self._SetLightBlock(playerId, intPos)

        return True

    def OnQuit(self, args):
        playerId = args["id"]
        # 清理玩家数据
        self.playerPos.pop(playerId, None)
        self.playerLightLevel.pop(playerId, None)

        # 移除光源方块
        self._RemoveLightBlock(playerId)

    def OnCarryNewItem(self, args):
        playerId = args.get("playerId")
        newItemDict = args.get("newItemDict")

        if not playerId or not newItemDict:
            return

        identifier = newItemDict.get("newItemName")
        lightLevel = self.LIGHT_MAPPING.get(identifier, 0)

        # 更新玩家的光照等级
        oldLightLevel = self.playerLightLevel.get(playerId, 0)

        if lightLevel != oldLightLevel:
            if lightLevel > 0:
                self.playerLightLevel[playerId] = lightLevel
            else:
                self.playerLightLevel.pop(playerId, None)

            # 立即更新光源
            self._UpdatePlayerLight(playerId)

    def Update(self):
        self.tickCounter += 1
        if self.tickCounter >= self.CHECK_INTERVAL:
            self.tickCounter = 0

            # 检查所有在线玩家的位置变化
            for playerId in serverApi.GetPlayerList():
                self.CheckPlayerPos(playerId)

    """
    检查玩家的整数坐标是否和上一个一致
    """

    def CheckPlayerPos(self, playerId):
        """检查单个玩家的位置变化"""
        posComp = serverApi.GetEngineCompFactory().CreatePos(playerId)
        pos = posComp.GetPos()
        # 转换为整数坐标
        intPos = tuple([int(floor(x)) for x in pos])

        # 检查位置是否发生变化
        oldPos = self.playerPos.get(playerId)
        if intPos != oldPos:
            self.playerPos[playerId] = intPos
            # 如果玩家有光源，更新光源位置
            if playerId in self.playerLightLevel:
                self._UpdatePlayerLight(playerId)
