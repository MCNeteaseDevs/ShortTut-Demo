# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi

ScreenNode = clientApi.GetScreenNodeCls()
ViewBinder = clientApi.GetViewBinderCls()

MOVER_PATHS = (
    "/root/linearColumn/mover",
    "/root/outCubicColumn/mover",
    "/root/inCubicColumn/mover",
    "/root/outBackColumn/mover",
)


class EasingCompareScreen(ScreenNode):

    def __init__(self, namespace, name, param):
        ScreenNode.__init__(self, namespace, name, param)

    @ViewBinder.binding(ViewBinder.BF_ButtonClickUp, "#replay_easing")
    def Replay(self, args):
        for path in MOVER_PATHS:
            control = self.GetBaseUIControl(path)
            if control:
                control.resetAnimation()

    @ViewBinder.binding(ViewBinder.BF_ButtonClickUp, "#close_easing")
    def Close(self, args):
        clientApi.PopScreen()
