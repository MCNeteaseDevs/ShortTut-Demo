# -*- coding: utf-8 -*-

import mod.client.extraClientApi as clientApi
import demoTpPointScript.tpPointConst as tpPointConst
import demoTpPointScript.ui.uiMgr as uiMgr
from demoTpPointScript.ui.uiDef import UIDef
from mod_log import logger

ClientSystem = clientApi.GetClientSystemCls()


class TpPointClientSystem(ClientSystem):
	"""
	客户端系统：
	- UI初始化后注册界面
	- 接收服务端事件打开/刷新传送点界面
	- 转发UI操作到服务端
	"""

	def __init__(self, namespace, systemName):
		ClientSystem.__init__(self, namespace, systemName)
		self.mUIMgr = uiMgr.UIMgr()

		# 监听引擎事件
		self.ListenForEvent(
			clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(),
			tpPointConst.UiInitFinishedEvent, self, self.OnUiInitFinished
		)
		# 监听服务端事件
		self.ListenForEvent(
			tpPointConst.ModName, tpPointConst.ServerSystemName,
			tpPointConst.OpenTpUIEvent, self, self.OnOpenTpUI
		)
		logger.info("TpPointClientSystem init")

	def Destroy(self):
		self.UnListenForEvent(
			clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(),
			tpPointConst.UiInitFinishedEvent, self, self.OnUiInitFinished
		)
		self.UnListenForEvent(
			tpPointConst.ModName, tpPointConst.ServerSystemName,
			tpPointConst.OpenTpUIEvent, self, self.OnOpenTpUI
		)
		if self.mUIMgr:
			self.mUIMgr.Destroy()

	# ---- 引擎事件 ----

	def OnUiInitFinished(self, args):
		logger.info("TpPointClientSystem OnUiInitFinished")
		self.mUIMgr.Init(self)

	# ---- 服务端事件处理 ----

	def OnOpenTpUI(self, args):
		"""服务端通知打开传送界面，携带传送点列表"""
		points = args.get("points", [])
		self.mUIMgr.PushScreen(UIDef.TpPointScreen, {"points": points})

	# ---- 客户端 → 服务端请求 ----

	def RequestAddTpPoint(self, name):
		self.NotifyToServer(tpPointConst.AddTpPointEvent, {"name": name})

	def RequestDeleteTpPoint(self, name):
		self.NotifyToServer(tpPointConst.DeleteTpPointEvent, {"name": name})

	def RequestTeleport(self, name):
		self.NotifyToServer(tpPointConst.TeleportEvent, {"name": name})
