# -*- coding: utf-8 -*-

import mod.server.extraServerApi as serverApi
import demoUI1Script.uI1Const as uI1Const
from mod_log import logger

ServerSystem = serverApi.GetServerSystemCls()

class UI1ServerSystem(ServerSystem):
	"""
	该mod的服务端类
	"""

	def __init__(self, namespace, systemName):
		ServerSystem.__init__(self, namespace, systemName)
