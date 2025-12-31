# -*- coding: utf-8 -*-

import mod.client.extraClientApi as clientApi
import demoSortScript.sortConst as SortConst
import demoSortScript.ui.uiMgr as uiMgr
from mod_log import logger

ClientSystem = clientApi.GetClientSystemCls()
NativeScreenManager = clientApi.GetNativeScreenManagerCls()


class SortClientSystem(ClientSystem):
    """
    该mod的客户端类
    根据服务端推送下来的数据显示通用显示界面
    """

    def __init__(self, namespace, systemName):
        ClientSystem.__init__(self, namespace, systemName)
        self.mUIMgr = uiMgr.UIMgr()
        self.currentOpenChestPos = (0, 0, 0)
        self.ListenForEvent(clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(), "ClientChestOpenEvent", self, self.OnChestOpen)
        self.ListenForEvent(clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(), SortConst.UiInitFinishedEvent, self, self.OnUiInitFinished)
        NativeScreenManager.instance().RegisterScreenProxy(
            "crafting.inventory_screen", "demoSortScript.ui.player_inventory_screen.PlayerInventoryScreen"
        )
        NativeScreenManager.instance().RegisterScreenProxy(
            "chest.small_chest_screen", "demoSortScript.ui.small_chest_screen.SmallChestScreen"
        )
        NativeScreenManager.instance().RegisterScreenProxy(
            "chest.large_chest_screen", "demoSortScript.ui.large_chest_screen.LargeChestScreen"
        )
        clientApi.GetEngineCompFactory().CreatePlayerView(clientApi.GetLevelId()).SetUIProfile(0)

    def Destroy(self):
        self.UnListenForEvent(clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(), SortConst.UiInitFinishedEvent, self, self.OnUiInitFinished)
        if self.mUIMgr:
            self.mUIMgr.Destroy()

    def RequestSort(self, type):
        self.NotifyToServer("RequestSortEvent", {"type": type, "pos": self.currentOpenChestPos})

    def OnChestOpen(self, args):
        if args["playerId"] != clientApi.GetLocalPlayerId():
            return
        self.currentOpenChestPos = (args["x"], args["y"], args["z"])

    # UI加载完成
    def OnUiInitFinished(self, args):
        logger.info("%s OnUiInitFinished", SortConst.ClientSystemName)
        self.mUIMgr.Init(self)
