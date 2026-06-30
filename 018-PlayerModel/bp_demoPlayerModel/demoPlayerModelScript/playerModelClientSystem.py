# -*- coding: utf-8 -*-

import mod.client.extraClientApi as clientApi
import demoPlayerModelScript.ui.uiMgr as uiMgr
from mod_log import logger
import demoPlayerModelScript.playerModelConst as playerModelConst


ClientSystem = clientApi.GetClientSystemCls()


class PlayerModelClientSystem(ClientSystem):
    """
    该mod的客户端类
    根据服务端推送下来的数据显示通用显示界面
    """

    def __init__(self, namespace, systemName):
        ClientSystem.__init__(self, namespace, systemName)
        self.mUIMgr = uiMgr.UIMgr()

        self.ListenForEvent(clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(), playerModelConst.UiInitFinishedEvent, self, self.OnUiInitFinished)
        self.ListenForEvent(clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(), "OnLocalPlayerStopLoading", self, self.OnLocalPlayerStopLoading)

    def Destroy(self):
        self.UnListenForEvent(clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(), playerModelConst.UiInitFinishedEvent, self, self.OnUiInitFinished)
        self.UnListenForEvent(clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(), "OnLocalPlayerStopLoading", self, self.OnLocalPlayerStopLoading)
        if self.mUIMgr:
            self.mUIMgr.Destroy()

    def OnLocalPlayerStopLoading(self, args):
        actorRenderComp = clientApi.GetEngineCompFactory().CreateActorRender(clientApi.GetLocalPlayerId())
        # 更换模型贴图
        actorRenderComp.AddPlayerGeometry('default', "geometry.custom_squirrel")
        actorRenderComp.AddPlayerTexture('default', "textures/entity/custom_squirrel")
        actorRenderComp.RebuildPlayerRender()
    # UI加载完成
    def OnUiInitFinished(self, args):
        logger.info("%s OnUiInitFinished", playerModelConst.ClientSystemName)