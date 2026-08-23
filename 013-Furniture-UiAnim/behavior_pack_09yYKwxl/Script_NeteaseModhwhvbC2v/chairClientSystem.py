# -*- coding: utf-8 -*-

import mod.client.extraClientApi as clientApi

import Script_NeteaseModhwhvbC2v.chairConst as chairConst


ClientSystem = clientApi.GetClientSystemCls()
CompFactory = clientApi.GetEngineCompFactory()


class ChairClientSystem(ClientSystem):

    def __init__(self, namespace, systemName):
        ClientSystem.__init__(self, namespace, systemName)
        self.mBlockInfoComp = CompFactory.CreateBlockInfo(clientApi.GetLevelId())
        self.mSpinningChairs = set()
        self.mSnapshotDimension = None
        self.mUIRegistered = False

        self.ListenForEvent(
            clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(),
            "UiInitFinished", self, self.OnUiInitFinished
        )
        self.ListenForEvent(
            clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(),
            "ModBlockEntityLoadedClientEvent", self, self.OnBlockEntityLoaded
        )
        self.ListenForEvent(
            chairConst.ModName, chairConst.ServerSystemName,
            chairConst.OpenChairUIEvent, self, self.OnOpenChairUI
        )
        self.ListenForEvent(
            chairConst.ModName, chairConst.ServerSystemName,
            chairConst.SyncChairSpinEvent, self, self.OnSyncChairSpin
        )
        self.ListenForEvent(
            chairConst.ModName, chairConst.ServerSystemName,
            chairConst.SyncChairSpinSnapshotEvent, self, self.OnSyncChairSpinSnapshot
        )

    def Destroy(self):
        self.UnListenForEvent(
            clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(),
            "UiInitFinished", self, self.OnUiInitFinished
        )
        self.UnListenForEvent(
            clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(),
            "ModBlockEntityLoadedClientEvent", self, self.OnBlockEntityLoaded
        )
        self.UnListenForEvent(
            chairConst.ModName, chairConst.ServerSystemName,
            chairConst.OpenChairUIEvent, self, self.OnOpenChairUI
        )
        self.UnListenForEvent(
            chairConst.ModName, chairConst.ServerSystemName,
            chairConst.SyncChairSpinEvent, self, self.OnSyncChairSpin
        )
        self.UnListenForEvent(
            chairConst.ModName, chairConst.ServerSystemName,
            chairConst.SyncChairSpinSnapshotEvent, self, self.OnSyncChairSpinSnapshot
        )

    def OnUiInitFinished(self, args):
        if self.mUIRegistered:
            return
        self.mUIRegistered = clientApi.RegisterUI(
            chairConst.ModName,
            chairConst.SpinScreenKey,
            chairConst.SpinScreenClsPath,
            chairConst.SpinScreenDef
        )

    def OnOpenChairUI(self, args):
        if not self.mUIRegistered:
            return
        clientApi.PushScreen(
            chairConst.ModName,
            chairConst.SpinScreenKey,
            {
                "dimensionId": args.get("dimensionId", -1),
                "blockPos": args.get("blockPos", [])
            }
        )

    def RequestSetChairSpin(self, dimensionId, blockPos, value):
        self.NotifyToServer(
            chairConst.SetChairSpinEvent,
            {
                "dimensionId": dimensionId,
                "blockPos": list(blockPos),
                "value": value
            }
        )

    def OnSyncChairSpin(self, args):
        state = self._ParseState(args)
        if state is None:
            return
        dimensionId, blockPos, value = state
        if self.mSnapshotDimension is not None and dimensionId != self.mSnapshotDimension:
            return
        self._CacheState(dimensionId, blockPos, value)
        self._ApplyState(dimensionId, blockPos, value)

    def OnSyncChairSpinSnapshot(self, args):
        try:
            snapshotDimension = int(args.get("dimensionId"))
        except (TypeError, ValueError):
            return

        oldStates = self.mSpinningChairs
        newStates = set()

        for rawState in args.get("states", []):
            state = self._ParseState(rawState)
            if state is None:
                continue
            dimensionId, blockPos, value = state
            if dimensionId == snapshotDimension and value > 0.0:
                newStates.add(self._MakeStateKey(dimensionId, blockPos))

        self.mSpinningChairs = newStates
        if self.mSnapshotDimension == snapshotDimension:
            for stateKey in oldStates - newStates:
                self._ApplyStateKey(stateKey, 0.0)
        self.mSnapshotDimension = snapshotDimension
        for stateKey in newStates:
            self._ApplyStateKey(stateKey, 1.0)

    def OnBlockEntityLoaded(self, args):
        if args.get("blockName") != chairConst.ChairBlockName:
            return
        state = self._ParseState({
            "dimensionId": args.get("dimensionId", -1),
            "blockPos": [args.get("posX"), args.get("posY"), args.get("posZ")],
            "value": 1.0
        })
        if state is None:
            return
        dimensionId, blockPos, unusedValue = state
        if self.mSnapshotDimension is not None and dimensionId != self.mSnapshotDimension:
            return
        stateKey = self._MakeStateKey(dimensionId, blockPos)
        value = 1.0 if stateKey in self.mSpinningChairs else 0.0
        self._ApplyState(dimensionId, blockPos, value)

    def _CacheState(self, dimensionId, blockPos, value):
        stateKey = self._MakeStateKey(dimensionId, blockPos)
        if value > 0.0:
            self.mSpinningChairs.add(stateKey)
        else:
            self.mSpinningChairs.discard(stateKey)

    def _ApplyStateKey(self, stateKey, value):
        dimensionId, x, y, z = stateKey
        self._ApplyState(dimensionId, (x, y, z), value)

    def _ApplyState(self, dimensionId, blockPos, value):
        self.mBlockInfoComp.SetEnableBlockEntityAnimations(blockPos, True)
        return self.mBlockInfoComp.SetBlockEntityMolangValue(
            blockPos,
            chairConst.ChairSpinVariable,
            value
        )

    @staticmethod
    def _ParseState(args):
        rawPos = args.get("blockPos")
        if not isinstance(rawPos, (list, tuple)) or len(rawPos) != 3:
            return None
        try:
            dimensionId = int(args.get("dimensionId", -1))
            blockPos = int(rawPos[0]), int(rawPos[1]), int(rawPos[2])
            value = 1.0 if float(args.get("value", 0.0)) > 0.0 else 0.0
        except (TypeError, ValueError):
            return None
        return dimensionId, blockPos, value

    @staticmethod
    def _MakeStateKey(dimensionId, blockPos):
        return dimensionId, blockPos[0], blockPos[1], blockPos[2]
