# -*- coding: utf-8 -*-

import mod.client.extraClientApi as clientApi
from mod.common.minecraftEnum import KeyBoardType
import demoUI1Script.ui.uiMgr as uiMgr
from mod_log import logger
import demoUI1Script.uI1Const as uI1Const
from demoUI1Script.ui.uiDef import UIDef
from demoUI1Script.uI1Const import ModName, ServerSystemName

ClientSystem = clientApi.GetClientSystemCls()


class UI1ClientSystem(ClientSystem):
    """
    该mod的客户端类
    根据服务端推送下来的数据显示通用显示界面
    """

    def __init__(self, namespace, systemName):
        ClientSystem.__init__(self, namespace, systemName)
        self.mUIMgr = uiMgr.UIMgr()

        self.ListenForEvent(clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(), uI1Const.UiInitFinishedEvent, self, self.OnUiInitFinished)
        self.ListenForEvent(clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(), "OnKeyPressInGame", self, self.OnKeyPress)
        self.ListenForEvent(ModName, ServerSystemName, "OpenEasingCompare", self, self.OnOpenEasingCompare)

    def Destroy(self):
        self.UnListenForEvent(clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(), uI1Const.UiInitFinishedEvent, self, self.OnUiInitFinished)
        self.UnListenForEvent(clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(), "OnKeyPressInGame", self, self.OnKeyPress)
        self.UnListenForEvent(ModName, ServerSystemName, "OpenEasingCompare", self, self.OnOpenEasingCompare)
        if self.mUIMgr:
            self.mUIMgr.Destroy()

    # UI加载完成
    def OnUiInitFinished(self, args):
        self.mUIMgr.Init(self)

    def OnOpenEasingCompare(self, args):
        self.mUIMgr.PushScreen(UIDef.EasingCompare)

    def OnKeyPress(self, args):
        if args.get("screenName") != "hud_screen":
            return
        if args.get("isDown") != "1":
            return
        if args.get("key") != str(KeyBoardType.KEY_C):
            return
        self.mUIMgr.PushScreen(UIDef.UI1Screen)
