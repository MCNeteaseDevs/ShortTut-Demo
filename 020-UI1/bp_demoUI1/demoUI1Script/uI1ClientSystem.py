# -*- coding: utf-8 -*-

import mod.client.extraClientApi as clientApi
import demoUI1Script.ui.uiMgr as uiMgr
from mod_log import logger
import demoUI1Script.uI1Const as uI1Const
from demoUI1Script.ui.uiDef import UIDef

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

    def Destroy(self):
        self.UnListenForEvent(clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(), uI1Const.UiInitFinishedEvent, self, self.OnUiInitFinished)
        if self.mUIMgr:
            self.mUIMgr.Destroy()

    # UI加载完成
    def OnUiInitFinished(self, args):
        self.mUIMgr.Init(self)
