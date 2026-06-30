# -*- coding: utf-8 -*-

import mod.server.extraServerApi as serverApi
import demoPlayerModelScript.playerModelConst as playerModelConst
from mod_log import logger

ServerSystem = serverApi.GetServerSystemCls()

class PlayerModelServerSystem(ServerSystem):
	"""
	该mod的服务端类
	"""

	def __init__(self, namespace, systemName):
		ServerSystem.__init__(self, namespace, systemName)
