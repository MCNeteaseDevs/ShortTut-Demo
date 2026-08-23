# -*- coding: utf-8 -*-

import mod.client.extraClientApi as clientApi

import Script_NeteaseModhwhvbC2v.chairConst as chairConst


ScreenNode = clientApi.GetScreenNodeCls()
ViewBinder = clientApi.GetViewBinderCls()


class SpinScreen(ScreenNode):

    def __init__(self, namespace, name, param):
        ScreenNode.__init__(self, namespace, name, param)
        param = param or {}
        self.mClientSystem = None
        self.mDimensionId = self._ParseDimension(param.get("dimensionId"))
        self.mBlockPos = self._ParseBlockPos(param.get("blockPos"))

    def Create(self):
        self.mClientSystem = clientApi.GetSystem(
            chairConst.ModName,
            chairConst.ClientSystemName
        )

    @ViewBinder.binding(ViewBinder.BF_ButtonClickUp, "#turn_on")
    def OnTurnOn(self, args):
        self._SetSpin(1.0)

    @ViewBinder.binding(ViewBinder.BF_ButtonClickUp, "#turn_off")
    def OnTurnOff(self, args):
        self._SetSpin(0.0)

    @ViewBinder.binding(ViewBinder.BF_ButtonClickUp, "#close")
    def OnClose(self, args):
        self.SetRemove()

    def _SetSpin(self, value):
        if self.mClientSystem is None or self.mBlockPos is None:
            return
        if self.mDimensionId < 0:
            return
        self.mClientSystem.RequestSetChairSpin(
            self.mDimensionId,
            self.mBlockPos,
            value
        )

    @staticmethod
    def _ParseDimension(rawDimension):
        try:
            return int(rawDimension)
        except (TypeError, ValueError):
            return -1

    @staticmethod
    def _ParseBlockPos(rawPos):
        if not isinstance(rawPos, (list, tuple)) or len(rawPos) != 3:
            return None
        try:
            return int(rawPos[0]), int(rawPos[1]), int(rawPos[2])
        except (TypeError, ValueError):
            return None
