# -*- coding: utf-8 -*-

ModVersion = "1.0.0"
ModName = "demoCamera"
ClientSystemName = "demoCameraBeh"
ClientSystemClsPath = "demoCameraScript.cameraClientSystem.CameraClientSystem"
ServerSystemName = "demoCameraDev"
ServerSystemClsPath = "demoCameraScript.cameraServerSystem.CameraServerSystem"

OnKeyPressInGameEvent = "OnKeyPressInGame"
HudScreenName = "hud_screen"

# OnKeyPressInGame 的 key 是字符串键码，对应 KeyBoardType.KEY_1/2/3
KEY_DEFAULT = "49"
KEY_OFFSET = "50"
KEY_SHOULDER = "51"

OFFSET_DEFAULT = (0.0, 0.0, 0.0)
ANCHOR_DEFAULT = (0.0, 0.0, 0.0)
# (左右, 上下, 前后)；若进游戏后镜头往左偏，把 OFFSET_SHOULDER 的第一项改成负数
OFFSET_SHOULDER = (1.0, 0.2, 0.0)
ANCHOR_SHOULDER = (0.0, 0.6, 0.0)
