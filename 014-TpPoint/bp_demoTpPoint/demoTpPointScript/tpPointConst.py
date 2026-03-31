# -*- coding: utf-8 -*-

# 整个Mod的一些绑定配置
ModVersion = "1.0.0"
ModName = "demoTpPoint"
ClientSystemName = "demoTpPointBeh"
ClientSystemClsPath = "demoTpPointScript.tpPointClientSystem.TpPointClientSystem"
ServerSystemName = "demoTpPointDev"
ServerSystemClsPath = "demoTpPointScript.tpPointServerSystem.TpPointServerSystem"

# 引擎事件
UiInitFinishedEvent = "UiInitFinished"

# 自定义事件 —— 服务端 → 客户端
OpenTpUIEvent = "OpenTpUIEvent"           # 服务端通知客户端打开传送界面，携带传送点列表
SyncTpPointsEvent = "SyncTpPointsEvent"   # 服务端同步传送点列表到客户端（增删后刷新）

# 自定义事件 —— 客户端 → 服务端
AddTpPointEvent = "AddTpPointEvent"       # 客户端请求新增传送点 {name: str}
DeleteTpPointEvent = "DeleteTpPointEvent" # 客户端请求删除传送点 {name: str}
TeleportEvent = "TeleportEvent"           # 客户端请求传送到指定点 {name: str}