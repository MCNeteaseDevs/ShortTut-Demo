# -*- coding: utf-8 -*-

import client.extraClientApi as clientApi
from mod_log import logger
from ActorBlockGeometryScripts.modCommon import modConfig

ScreenNode = clientApi.GetScreenNodeCls()


class MainScreen(ScreenNode):
    def __init__(self, namespace, name, param):
        ScreenNode.__init__(self, namespace, name, param)
        self.mButtonPanelItem = None
        self.mCombButtonItem = None
        self.mReleaseButtonItem = None
        # 面板
        self.mButtonPanel = "/buttonPanel"

        # 按钮
        self.mCombButton = "/button0"
        self.mReleaseButton = "/button1"

    def Create(self):
        logger.info("===== MainScreen Create =====")

        self.mButtonPanelItem = self.GetBaseUIControl(self.mButtonPanel)
        self.mCombButtonItem = self.mButtonPanelItem.GetChildByName(self.mCombButton).asButton()
        self.mReleaseButtonItem = self.mButtonPanelItem.GetChildByName(self.mReleaseButton).asButton()

        self.mCombButtonItem.AddTouchEventParams({"isSwallow": True, "myParams": 1})
        self.mCombButtonItem.SetButtonTouchUpCallback(self.OnCombBlockTouch)

        self.mReleaseButtonItem.AddTouchEventParams({"isSwallow": True, "myParams": 1})
        self.mReleaseButtonItem.SetButtonTouchUpCallback(self.OnReleaseBlockTouch)

    def OnCombBlockTouch(self, args):
        clientSystem = clientApi.GetSystem(modConfig.modName, modConfig.modClientSystem)
        clientSystem.SendGetBlockPalette()

    def OnReleaseBlockTouch(self, args):
        clientSystem = clientApi.GetSystem(modConfig.modName, modConfig.modClientSystem)
        clientSystem.SendDestoryBlockPalette()

    def OnOpenCloseButtonPanel(self):
        if self.mButtonPanelItem.GetVisible():
            self.mButtonPanelItem.SetVisible(False)
        else:
            self.mButtonPanelItem.SetVisible(True)

    def OnCloseButtonPanel(self):
        self.mButtonPanelItem.SetVisible(False)