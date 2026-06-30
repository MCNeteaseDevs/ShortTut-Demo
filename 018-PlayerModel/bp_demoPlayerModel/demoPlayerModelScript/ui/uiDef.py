# -*- coding: utf-8 -*-
import mod.client.extraClientApi as extraClientApi


class UIDef:
    PlayerModelScreen = "PlayerModelScreen"


UIData = {
    UIDef.PlayerModelScreen: {
        "cls": "demoPlayerModelScript.ui.demo_playerModel_screen.PlayerModelScreen",
        "screen": "demo_playerModel_screen.main",
        "version": 1,  # version 1代表使用CreateUI方式创建的UI，需要设置isHud,layer。2代使用PushScreen创建的ui，不需要额外设置
        "layer": extraClientApi.GetMinecraftEnum().UiBaseLayer.Desk,
        "isHud": 1
    }
}
