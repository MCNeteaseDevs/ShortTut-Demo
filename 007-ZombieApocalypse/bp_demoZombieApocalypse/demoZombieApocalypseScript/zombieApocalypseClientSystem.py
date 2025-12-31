# -*- coding: utf-8 -*-

import mod.client.extraClientApi as clientApi
import demoZombieApocalypseScript.zombieApocalypseConst as ZombieApocalypseConst
import demoZombieApocalypseScript.ui.uiMgr as uiMgr
from mod_log import logger

ClientSystem = clientApi.GetClientSystemCls()


class ZombieApocalypseClientSystem(ClientSystem):
    """
    该mod的客户端类
    根据服务端推送下来的数据显示通用显示界面
    """

    def __init__(self, namespace, systemName):
        ClientSystem.__init__(self, namespace, systemName)
        self.mUIMgr = uiMgr.UIMgr()
        self.gameComp = clientApi.GetEngineCompFactory().CreateGame(clientApi.GetLevelId())
        self.ListenForEvent(clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(), ZombieApocalypseConst.UiInitFinishedEvent, self, self.OnUiInitFinished)

    def Destroy(self):
        self.UnListenForEvent(clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(), ZombieApocalypseConst.UiInitFinishedEvent, self, self.OnUiInitFinished)
        if self.mUIMgr:
            self.mUIMgr.Destroy()

    # UI加载完成
    def OnUiInitFinished(self, args):
        logger.info("%s OnUiInitFinished", ZombieApocalypseConst.ClientSystemName)