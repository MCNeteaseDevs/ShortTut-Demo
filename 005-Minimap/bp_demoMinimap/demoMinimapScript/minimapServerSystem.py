# -*- coding: utf-8 -*-

import mod.server.extraServerApi as serverApi
import demoMinimapScript.minimapConst as minimapConst
from mod_log import logger

ServerSystem = serverApi.GetServerSystemCls()

class MinimapServerSystem(ServerSystem):
	"""
	该mod的服务端类
	"""

	def __init__(self, namespace, systemName):
		ServerSystem.__init__(self, namespace, systemName)
