# -*- coding: utf-8 -*-

import time

import mod.server.extraServerApi as serverApi

import Script_NeteaseModhwhvbC2v.chairConst as chairConst


ServerSystem = serverApi.GetServerSystemCls()
CompFactory = serverApi.GetEngineCompFactory()


class ChairServerSystem(ServerSystem):

    def __init__(self, namespace, systemName):
        ServerSystem.__init__(self, namespace, systemName)
        self.mBlockInfoComp = CompFactory.CreateBlockInfo(serverApi.GetLevelId())
        self.mSpinningChairs = set()
        self.mLastOpenTime = {}

        self.ListenForEvent(
            serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(),
            "ServerBlockUseEvent", self, self.OnServerBlockUse
        )
        self.ListenForEvent(
            serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(),
            "ClientLoadAddonsFinishServerEvent", self, self.OnClientLoadFinished
        )
        self.ListenForEvent(
            serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(),
            "BlockRemoveServerEvent", self, self.OnBlockRemove
        )
        self.ListenForEvent(
            serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(),
            "DimensionChangeFinishServerEvent", self, self.OnDimensionChangeFinished
        )
        self.ListenForEvent(
            chairConst.ModName, chairConst.ClientSystemName,
            chairConst.SetChairSpinEvent, self, self.OnSetChairSpin
        )

        self.mBlockInfoComp.ListenOnBlockRemoveEvent(chairConst.ChairBlockName, True)

    def Destroy(self):
        self.mBlockInfoComp.ListenOnBlockRemoveEvent(chairConst.ChairBlockName, False)
        self.UnListenForEvent(
            serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(),
            "ServerBlockUseEvent", self, self.OnServerBlockUse
        )
        self.UnListenForEvent(
            serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(),
            "ClientLoadAddonsFinishServerEvent", self, self.OnClientLoadFinished
        )
        self.UnListenForEvent(
            serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(),
            "BlockRemoveServerEvent", self, self.OnBlockRemove
        )
        self.UnListenForEvent(
            serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(),
            "DimensionChangeFinishServerEvent", self, self.OnDimensionChangeFinished
        )
        self.UnListenForEvent(
            chairConst.ModName, chairConst.ClientSystemName,
            chairConst.SetChairSpinEvent, self, self.OnSetChairSpin
        )

    def OnServerBlockUse(self, args):
        if args.get("blockName") != chairConst.ChairBlockName:
            return

        args["cancel"] = True
        playerId = args.get("playerId")
        blockPos = self._ParseBlockPos([
            args.get("x"), args.get("y"), args.get("z")
        ])
        if not playerId or blockPos is None:
            return

        dimensionId = self._GetPlayerDimension(playerId)
        if dimensionId is None:
            return

        now = time.time()
        if now - self.mLastOpenTime.get(playerId, 0.0) < 0.5:
            return
        self.mLastOpenTime[playerId] = now

        self.NotifyToClient(
            playerId,
            chairConst.OpenChairUIEvent,
            {
                "dimensionId": dimensionId,
                "blockPos": list(blockPos)
            }
        )

    def OnSetChairSpin(self, args):
        playerId = args.get("__id__")
        blockPos = self._ParseBlockPos(args.get("blockPos"))
        if not playerId or blockPos is None:
            return

        try:
            requestedDimension = int(args.get("dimensionId", -1))
        except (TypeError, ValueError):
            return

        playerDimension = self._GetPlayerDimension(playerId)
        if playerDimension is None:
            return
        if requestedDimension != playerDimension:
            return

        blockDict = self.mBlockInfoComp.GetBlockNew(blockPos, playerDimension)
        if not blockDict or blockDict.get("name") != chairConst.ChairBlockName:
            return

        try:
            value = 1.0 if float(args.get("value", 0.0)) > 0.0 else 0.0
        except (TypeError, ValueError):
            return
        stateKey = self._MakeStateKey(playerDimension, blockPos)
        if value > 0.0:
            self.mSpinningChairs.add(stateKey)
        else:
            self.mSpinningChairs.discard(stateKey)

        self._BroadcastChairState(playerDimension, blockPos, value)

    def OnClientLoadFinished(self, args):
        playerId = args.get("playerId")
        if not playerId:
            return
        self._SendSnapshot(playerId)

    def OnDimensionChangeFinished(self, args):
        playerId = args.get("playerId")
        if not playerId:
            return
        self._SendSnapshot(playerId)

    def _SendSnapshot(self, playerId):
        playerDimension = self._GetPlayerDimension(playerId)
        if playerDimension is None:
            return
        states = []
        for dimensionId, x, y, z in sorted(self.mSpinningChairs):
            if dimensionId != playerDimension:
                continue
            states.append({
                "dimensionId": dimensionId,
                "blockPos": [x, y, z],
                "value": 1.0
            })
        self.NotifyToClient(
            playerId,
            chairConst.SyncChairSpinSnapshotEvent,
            {
                "dimensionId": playerDimension,
                "states": states
            }
        )

    def OnBlockRemove(self, args):
        if args.get("fullName") != chairConst.ChairBlockName:
            return

        blockPos = self._ParseBlockPos([
            args.get("x"), args.get("y"), args.get("z")
        ])
        dimensionId = args.get("dimension")
        if blockPos is None or dimensionId is None:
            return
        stateKey = self._MakeStateKey(dimensionId, blockPos)
        if stateKey not in self.mSpinningChairs:
            return

        self.mSpinningChairs.discard(stateKey)
        self._BroadcastChairState(dimensionId, blockPos, 0.0)

    def _BroadcastChairState(self, dimensionId, blockPos, value):
        eventData = {
            "dimensionId": dimensionId,
            "blockPos": list(blockPos),
            "value": value
        }
        for playerId in serverApi.GetPlayerList():
            if self._GetPlayerDimension(playerId) == dimensionId:
                self.NotifyToClient(
                    playerId,
                    chairConst.SyncChairSpinEvent,
                    eventData
                )

    @staticmethod
    def _GetPlayerDimension(playerId):
        dimensionComp = CompFactory.CreateDimension(playerId)
        return dimensionComp.GetEntityDimensionId()

    @staticmethod
    def _ParseBlockPos(rawPos):
        if not isinstance(rawPos, (list, tuple)) or len(rawPos) != 3:
            return None
        try:
            return int(rawPos[0]), int(rawPos[1]), int(rawPos[2])
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _MakeStateKey(dimensionId, blockPos):
        return dimensionId, blockPos[0], blockPos[1], blockPos[2]
