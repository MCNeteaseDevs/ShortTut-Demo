# -*- coding: utf-8 -*-

import mod.client.extraClientApi as clientApi
import demoPotionScript.potionConst as potionConst
import demoPotionScript.ui.uiMgr as uiMgr
from mod_log import logger

ClientSystem = clientApi.GetClientSystemCls()
CompFactory = clientApi.GetEngineCompFactory()


class PotionClientSystem(ClientSystem):
	"""
	该mod的客户端类
	服务端通知落点后，在滞留云的位置播放粒子。
	"""

	def __init__(self, namespace, systemName):
		ClientSystem.__init__(self, namespace, systemName)
		self.mUIMgr = uiMgr.UIMgr()
		self.mParticleComp = CompFactory.CreateParticleSystem(None)
		self.mParticleId = 0
		self.ListenForEvent(
			clientApi.GetEngineNamespace(),
			clientApi.GetEngineSystemName(),
			potionConst.UiInitFinishedEvent,
			self,
			self.OnUiInitFinished
		)
		self.ListenForEvent(
			potionConst.ModName,
			potionConst.ServerSystemName,
			potionConst.ShowCloudVisualEvent,
			self,
			self.OnShowCloud
		)
		self.ListenForEvent(
			potionConst.ModName,
			potionConst.ServerSystemName,
			potionConst.ClearCloudVisualEvent,
			self,
			self.OnClearCloud
		)

	def Destroy(self):
		self.UnListenForEvent(
			clientApi.GetEngineNamespace(),
			clientApi.GetEngineSystemName(),
			potionConst.UiInitFinishedEvent,
			self,
			self.OnUiInitFinished
		)
		self.UnListenForEvent(
			potionConst.ModName,
			potionConst.ServerSystemName,
			potionConst.ShowCloudVisualEvent,
			self,
			self.OnShowCloud
		)
		self.UnListenForEvent(
			potionConst.ModName,
			potionConst.ServerSystemName,
			potionConst.ClearCloudVisualEvent,
			self,
			self.OnClearCloud
		)
		self._RemoveParticle()
		if self.mUIMgr:
			self.mUIMgr.Destroy()

	def OnUiInitFinished(self, args):
		logger.info("%s OnUiInitFinished", potionConst.ClientSystemName)

	def OnShowCloud(self, args):
		if "x" not in args or "y" not in args or "z" not in args:
			return
		self._RemoveParticle()
		if self.mParticleComp is None:
			return
		centerY = args["y"] + potionConst.HEIGHT * 0.5
		particleId = self.mParticleComp.Create(
			potionConst.PARTICLE_NAME,
			(args["x"], centerY, args["z"]),
			(0, 0, 0)
		)
		if not particleId:
			logger.info("%s lingering particle create failed", potionConst.ClientSystemName)
			return
		self.mParticleId = particleId

	def OnClearCloud(self, args):
		self._RemoveParticle()

	def _RemoveParticle(self):
		if not self.mParticleId or self.mParticleComp is None:
			self.mParticleId = 0
			return
		self.mParticleComp.Remove(self.mParticleId)
		self.mParticleId = 0
