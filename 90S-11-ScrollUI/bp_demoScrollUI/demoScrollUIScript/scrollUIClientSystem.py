# -*- coding: utf-8 -*-

import mod.client.extraClientApi as clientApi
import demoScrollUIScript.scrollUIConst as scrollUIConst
import demoScrollUIScript.ui.uiMgr as uiMgr
from demoScrollUIScript.ui.uiDef import UIDef
from mod_log import logger

ClientSystem = clientApi.GetClientSystemCls()


class ScrollUIClientSystem(ClientSystem):
	"""
	该mod的客户端类
	UI加载完成后打开滚动列表界面，关掉以后按 L 可以重新打开
	"""

	def __init__(self, namespace, systemName):
		ClientSystem.__init__(self, namespace, systemName)
		self.mUIMgr = uiMgr.UIMgr()

		self.ListenForEvent(
			clientApi.GetEngineNamespace(),
			clientApi.GetEngineSystemName(),
			scrollUIConst.UiInitFinishedEvent,
			self,
			self.OnUiInitFinished
		)
		self.ListenForEvent(
			clientApi.GetEngineNamespace(),
			clientApi.GetEngineSystemName(),
			scrollUIConst.OnKeyPressInGameEvent,
			self,
			self.OnKeyPressInGame
		)

	def Destroy(self):
		self.UnListenForEvent(
			clientApi.GetEngineNamespace(),
			clientApi.GetEngineSystemName(),
			scrollUIConst.UiInitFinishedEvent,
			self,
			self.OnUiInitFinished
		)
		self.UnListenForEvent(
			clientApi.GetEngineNamespace(),
			clientApi.GetEngineSystemName(),
			scrollUIConst.OnKeyPressInGameEvent,
			self,
			self.OnKeyPressInGame
		)
		if self.mUIMgr:
			self.mUIMgr.Destroy()

	# UI加载完成
	def OnUiInitFinished(self, args):
		logger.info("%s OnUiInitFinished", scrollUIConst.ClientSystemName)
		self.mUIMgr.Init(self)
		self.mUIMgr.PushScreen(UIDef.ScrollUIScreen)

	def OnKeyPressInGame(self, args):
		if args.get("screenName") != scrollUIConst.HudScreenName:
			return
		if str(args.get("isDown")) != "1":
			return
		if str(args.get("key")) != scrollUIConst.KeyOpenUI:
			return
		self.mUIMgr.PushScreen(UIDef.ScrollUIScreen)
