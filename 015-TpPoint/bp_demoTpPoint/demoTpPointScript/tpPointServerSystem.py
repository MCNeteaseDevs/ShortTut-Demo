# -*- coding: utf-8 -*-

import mod.server.extraServerApi as serverApi
import demoTpPointScript.tpPointConst as tpPointConst
from mod_log import logger

ServerSystem = serverApi.GetServerSystemCls()


class TpPointServerSystem(ServerSystem):
	"""
	服务端系统：
	- 监听聊天命令 home 打开传送点界面
	- 存储每个玩家的传送点数据
	- 处理新增/删除/传送请求
	"""

	def __init__(self, namespace, systemName):
		ServerSystem.__init__(self, namespace, systemName)
		# 每个玩家的传送点数据: {playerId: {pointName: {"pos": (x,y,z), "dimId": int}, ...}}
		self.mTpPoints = {}

		# 监听聊天事件
		self.ListenForEvent(
			serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(),
			"ServerChatEvent", self, self.OnServerChat
		)
		# 监听客户端事件
		self.ListenForEvent(
			tpPointConst.ModName, tpPointConst.ClientSystemName,
			tpPointConst.AddTpPointEvent, self, self.OnAddTpPoint
		)
		self.ListenForEvent(
			tpPointConst.ModName, tpPointConst.ClientSystemName,
			tpPointConst.DeleteTpPointEvent, self, self.OnDeleteTpPoint
		)
		self.ListenForEvent(
			tpPointConst.ModName, tpPointConst.ClientSystemName,
			tpPointConst.TeleportEvent, self, self.OnTeleport
		)
		logger.info("TpPointServerSystem init")

	def Destroy(self):
		self.UnListenForEvent(
			serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(),
			"ServerChatEvent", self, self.OnServerChat
		)
		self.UnListenForEvent(
			tpPointConst.ModName, tpPointConst.ClientSystemName,
			tpPointConst.AddTpPointEvent, self, self.OnAddTpPoint
		)
		self.UnListenForEvent(
			tpPointConst.ModName, tpPointConst.ClientSystemName,
			tpPointConst.DeleteTpPointEvent, self, self.OnDeleteTpPoint
		)
		self.UnListenForEvent(
			tpPointConst.ModName, tpPointConst.ClientSystemName,
			tpPointConst.TeleportEvent, self, self.OnTeleport
		)

	# ---- 聊天命令 ----

	def OnServerChat(self, args):
		message = args.get("message", "").strip()
		playerId = args.get("playerId", "")
		if message == "home":
			args["cancel"] = True
			self._SendTpPointsToClient(playerId, openUI=True)

	# ---- 客户端请求处理 ----

	def OnAddTpPoint(self, args):
		playerId = args.get("__id__", "")
		name = args.get("name", "").strip()
		if not name:
			return
		# 获取玩家脚底坐标和维度
		posComp = serverApi.GetEngineCompFactory().CreatePos(playerId)
		pos = posComp.GetFootPos()
		if pos is None:
			return
		dimComp = serverApi.GetEngineCompFactory().CreateDimension(playerId)
		dimId = dimComp.GetEntityDimensionId()
		if playerId not in self.mTpPoints:
			self.mTpPoints[playerId] = {}
		self.mTpPoints[playerId][name] = {"pos": pos, "dimId": dimId}
		logger.info("AddTpPoint player=%s name=%s pos=%s dim=%s", playerId, name, pos, dimId)
		self._SendTpPointsToClient(playerId)

	def OnDeleteTpPoint(self, args):
		playerId = args.get("__id__", "")
		name = args.get("name", "")
		points = self.mTpPoints.get(playerId, {})
		if name in points:
			del points[name]
			logger.info("DeleteTpPoint player=%s name=%s", playerId, name)
		self._SendTpPointsToClient(playerId)

	def OnTeleport(self, args):
		playerId = args.get("__id__", "")
		name = args.get("name", "")
		points = self.mTpPoints.get(playerId, {})
		pointData = points.get(name)
		if pointData is None:
			return
		pos = pointData["pos"]
		targetDimId = pointData["dimId"]
		# 判断是否需要跨维度传送
		dimComp = serverApi.GetEngineCompFactory().CreateDimension(playerId)
		curDimId = dimComp.GetEntityDimensionId()
		if curDimId != targetDimId:
			dimComp.ChangePlayerDimension(targetDimId, (int(pos[0]), int(pos[1]), int(pos[2])))
		else:
			posComp = serverApi.GetEngineCompFactory().CreatePos(playerId)
			posComp.SetFootPos(pos)
		logger.info("Teleport player=%s name=%s pos=%s dim=%s", playerId, name, pos, targetDimId)

	# ---- 内部方法 ----

	def _SendTpPointsToClient(self, playerId, openUI=False):
		"""将传送点列表发送给客户端"""
		points = self.mTpPoints.get(playerId, {})
		# 转为列表格式方便客户端使用
		pointList = []
		for name, data in points.items():
			pointList.append({
				"name": name,
				"pos": list(data["pos"]),
				"dimId": data["dimId"]
			})
		eventName = tpPointConst.OpenTpUIEvent if openUI else tpPointConst.SyncTpPointsEvent
		self.NotifyToClient(playerId, eventName, {"points": pointList})
