# -*- coding: utf-8 -*-


class UIDef:
    ScrollUIScreen = "ScrollUIScreen"


UIData = {
    UIDef.ScrollUIScreen: {
        "cls": "demoScrollUIScript.ui.demo_scrollUI_screen.ScrollUIScreen",
        "screen": "demo_scrollUI_screen.main",
        # version 2 表示用 PushScreen 打开，不需要再设置 isHud / layer
        "version": 2
    }
}
