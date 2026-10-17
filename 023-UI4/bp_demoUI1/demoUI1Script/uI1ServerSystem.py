# -*- coding: utf-8 -*-

import mod.server.extraServerApi as serverApi
import demoUI1Script.uI1Const as uI1Const
from mod_log import logger

ServerSystem = serverApi.GetServerSystemCls()

CHAT_COMMANDS = {
	"easing": "OpenEasingCompare",
}

class UI1ServerSystem(ServerSystem):
	"""
	该mod的服务端类
	"""

	def __init__(self, namespace, systemName):
		ServerSystem.__init__(self, namespace, systemName)
		self.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), "ServerChatEvent", self, self.OnServerChat)

	def Destroy(self):
		self.UnListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), "ServerChatEvent", self, self.OnServerChat)

	def OnServerChat(self, args):
		message = args.get("message", "").strip().lower()
		eventName = CHAT_COMMANDS.get(message)
		if not eventName:
			return
		args["cancel"] = True
		playerId = args.get("playerId")
		if playerId:
			self.NotifyToClient(playerId, eventName, self.CreateEventData())
