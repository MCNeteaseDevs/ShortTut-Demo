# -*- coding: utf-8 -*-

import mod.server.extraServerApi as serverApi
import demoInstantBuildScript.instantBuildConst as instantBuildConst
from mod.common.minecraftEnum import Facing, AnimationModeType
from mod_log import logger

ServerSystem = serverApi.GetServerSystemCls()


class InstantBuildServerSystem(ServerSystem):
    """
    该mod的服务端类
    """

    def __init__(self, namespace, systemName):
        ServerSystem.__init__(self, namespace, systemName)
        self.gameComp = serverApi.GetEngineCompFactory().CreateGame(serverApi.GetLevelId())
        self.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), "ItemUseOnAfterServerEvent", self, self.OnUseItem)

    def OnUseItem(self, args):
        itemDict = args["itemDict"]
        if not itemDict:
            return
        itemName = itemDict["newItemName"]
        if itemName != "demo:shell_house_item":
            return
        pos = (args["x"], args["y"], args["z"])
        face = args["face"]
        target = self._GetFacing(pos, face)
        dim = args["dimensionId"]
        self.gameComp.PlaceStructure(None, target, "demo:shell_house", dim, 0, AnimationModeType.BLOCKS, 2.0)

    def _GetFacing(self, pos, face):
        x, y, z = pos
        if face == Facing.Up:
            y += 1
        elif face == Facing.Down:
            y -= 1
        elif face == Facing.North:
            z -= 1
        elif face == Facing.South:
            z += 1
        elif face == Facing.West:
            x -= 1
        elif face == Facing.East:
            x += 1
        return x, y, z
