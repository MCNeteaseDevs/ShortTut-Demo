# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi

from demoSortScript.sortConst import ModName, ClientSystemName

ScreenNode = clientApi.GetScreenNodeCls()
CustomUIScreenProxy = clientApi.GetUIScreenProxyCls()
ViewBinder = clientApi.GetViewBinderCls()


class ChestSortBaseScreen(CustomUIScreenProxy):
    """
    ChestSortBaseScreen
    """

    def __init__(self, namespace, name):
        CustomUIScreenProxy.__init__(self, namespace, name)
        print '==== %s ====' % 'init ChestSortBaseScreen'
        self.screen = None
        self.clientSystem = None

    def OnCreate(self):
        print '==== %s ====' % 'ChestSortBaseScreen Create'
        self.screen = self.GetScreenNode()
        self.clientSystem = clientApi.GetSystem(ModName, ClientSystemName)

    def RequestSort(self):
        print "not implemented"

    @ViewBinder.binding(ViewBinder.BF_ButtonClickUp)
    def OnSortClick(self, args):
        self.RequestSort()
