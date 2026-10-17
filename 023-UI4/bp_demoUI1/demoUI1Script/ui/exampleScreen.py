# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi

ScreenNode = clientApi.GetScreenNodeCls()
ViewBinder = clientApi.GetViewBinderCls()
ViewRequest = clientApi.GetViewViewRequestCls()


class ExampleScreen(ScreenNode):

    def __init__(self, namespace, name, param):
        ScreenNode.__init__(self, namespace, name, param)
        self.count = 0

    @ViewBinder.binding(ViewBinder.BF_ButtonClickUp, "#add_count")
    def AddCount(self, args):
        self.count += 1
        return ViewRequest.Refresh

    @ViewBinder.binding(ViewBinder.BF_ButtonClickUp, "#close_counter")
    def Close(self, args):
        clientApi.PopScreen()

    @ViewBinder.binding(ViewBinder.BF_BindString, "#counter_text")
    def GetCounterText(self):
        return str(self.count)
