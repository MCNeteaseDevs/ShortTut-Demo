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

	界面里不放任何控制按钮，滚动全部由快捷键驱动：
	- L      开 / 关界面
	- 1      百分比跳到 0（顶部）
	- 2      百分比跳到 100（底部）
	- 3      读当前百分比再 +10
	- 4      像素定位到选中条目
	- 5      读回当前百分比 / 像素位置
	- 6      读回内容路径 / 内容控件
	1~6 只在界面打开时生效，界面关着时不影响正常游戏。
	"""

	def __init__(self, namespace, systemName):
		ClientSystem.__init__(self, namespace, systemName)
		self.mUIMgr = uiMgr.UIMgr()
		# 当前打开的界面实例，None 表示界面没开
		self.mScreen = None

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
		self.ListenForEvent(
			clientApi.GetEngineNamespace(),
			clientApi.GetEngineSystemName(),
			scrollUIConst.PopScreenEvent,
			self,
			self.OnPopScreen
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
		self.UnListenForEvent(
			clientApi.GetEngineNamespace(),
			clientApi.GetEngineSystemName(),
			scrollUIConst.PopScreenEvent,
			self,
			self.OnPopScreen
		)
		if self.mUIMgr:
			self.mUIMgr.Destroy()

	# UI加载完成
	def OnUiInitFinished(self, args):
		logger.info("%s OnUiInitFinished", scrollUIConst.ClientSystemName)
		self.mUIMgr.Init(self)
		self.OpenScreen()

	# ---------- 开 / 关界面 ----------

	def OpenScreen(self):
		if self.mScreen:
			return
		screen = self.mUIMgr.PushScreen(UIDef.ScrollUIScreen)
		if not screen:
			logger.info("%s PushScreen fail", scrollUIConst.ClientSystemName)
			return
		self.mScreen = screen

	def CloseScreen(self):
		if not self.mScreen:
			return
		# PopScreen 成功就自己清引用；PopScreenEvent 也会清一次，重复清没有副作用
		if clientApi.PopScreen():
			self.mScreen = None

	# 界面被移除时（按 L 关、按 ESC 关都走这里）把状态清干净
	def OnPopScreen(self, args):
		if args.get("screenDef") != scrollUIConst.ScrollUIScreenDef:
			return
		self.mScreen = None

	# ---------- 快捷键 ----------

	def OnKeyPressInGame(self, args):
		if str(args.get("isDown")) != "1":
			return
		key = str(args.get("key"))

		# L 只管开 / 关，界面开着关着都要能响应
		if key == scrollUIConst.KeyOpenUI:
			if self.mScreen:
				self.CloseScreen()
			else:
				self.OpenScreen()
			return

		# 1~6 只在界面打开时生效：界面没开就不响应，不影响正常挖方块
		if not self.mScreen:
			return
		if key == scrollUIConst.KeyToTop:
			self.mScreen.SetPercent(0)
		elif key == scrollUIConst.KeyToBottom:
			self.mScreen.SetPercent(100)
		elif key == scrollUIConst.KeyStepDown:
			self.mScreen.StepPercent(10)
		elif key == scrollUIConst.KeyLocate:
			self.mScreen.LocateSelected()
		elif key == scrollUIConst.KeyReadPos:
			self.mScreen.ReadPos()
		elif key == scrollUIConst.KeyContent:
			self.mScreen.ReadContentPath()
