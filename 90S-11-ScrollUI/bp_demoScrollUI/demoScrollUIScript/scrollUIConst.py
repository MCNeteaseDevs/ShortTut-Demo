# -*- coding: utf-8 -*-

# 整个Mod的一些绑定配置
ModVersion = "1.0.0"
ModName = "demoScrollUI"
ClientSystemName = "demoScrollUIBeh"
ClientSystemClsPath = "demoScrollUIScript.scrollUIClientSystem.ScrollUIClientSystem"
ServerSystemName = "demoScrollUIDev"
ServerSystemClsPath = "demoScrollUIScript.scrollUIServerSystem.ScrollUIServerSystem"

# 引擎事件
UiInitFinishedEvent = "UiInitFinished"
OnKeyPressInGameEvent = "OnKeyPressInGame"
PopScreenEvent = "PopScreenEvent"

# PopScreenEvent 里的 screenDef 是 namespace.screenName，用来判断关掉的是不是我们这个界面
ScrollUIScreenDef = "demo_scrollUI_screen.main"

# OnKeyPressInGame 的 key 是字符串键码，对应 mod.common.minecraftEnum.KeyBoardType
KeyOpenUI = "76"      # L：开 / 关界面
KeyToTop = "49"       # 1：SetScrollViewPercentValue(0)
KeyToBottom = "50"    # 2：SetScrollViewPercentValue(100)
KeyStepDown = "51"    # 3：GetScrollViewPercentValue() 再 +10
KeyLocate = "52"      # 4：SetScrollViewPos(选中下标 × 行高)
KeyReadPos = "53"     # 5：GetScrollViewPercentValue() + GetScrollViewPos()
KeyContent = "54"     # 6：GetScrollViewContentPath() + GetScrollViewContentControl()
