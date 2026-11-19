# -*- coding: utf-8 -*-

import mod.server.extraServerApi as serverApi
import demoScrollUIScript.scrollUIConst as scrollUIConst
from mod_log import logger

ServerSystem = serverApi.GetServerSystemCls()

class ScrollUIServerSystem(ServerSystem):
	"""
	该mod的服务端类
	"""

	def __init__(self, namespace, systemName):
		ServerSystem.__init__(self, namespace, systemName)
