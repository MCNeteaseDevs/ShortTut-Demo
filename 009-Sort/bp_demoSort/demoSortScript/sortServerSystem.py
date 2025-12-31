# -*- coding: utf-8 -*-

import mod.server.extraServerApi as serverApi
import demoSortScript.sortConst as sortConst
from mod_log import logger

from demoSortScript.util import SortableType

ServerSystem = serverApi.GetServerSystemCls()


class SortServerSystem(ServerSystem):
    """
    该mod的服务端类
    """

    def __init__(self, namespace, systemName):
        ServerSystem.__init__(self, namespace, systemName)
        self.chestBlockComp = serverApi.GetEngineCompFactory().CreateChestBlock(serverApi.GetLevelId())
        self.itemComp = serverApi.GetEngineCompFactory().CreateItem(serverApi.GetLevelId())
        self.blockInfoComp = serverApi.GetEngineCompFactory().CreateBlockInfo(serverApi.GetLevelId())
        self.ListenForEvent(sortConst.ModName, sortConst.ClientSystemName, "RequestSortEvent", self, self.OnRequestSort)

    def OnRequestSort(self, args):
        print "OnRequestSort", args
        type = args["type"]
        player = args["__id__"]
        sortable = SortableType.get(type)
        if not sortable:
            return
        sortable.Update({
            "player": player,
            "pos": args.get("pos"),
            "dim": serverApi.GetEngineCompFactory().CreateDimension(player).GetEntityDimensionId()
        })
        sortable.DoSort()
