# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi

from demoSortScript.ui.chest_sort_base_screen import ChestSortBaseScreen

ScreenNode = clientApi.GetScreenNodeCls()
CustomUIScreenProxy = clientApi.GetUIScreenProxyCls()
ViewBinder = clientApi.GetViewBinderCls()


class LargeChestScreen(ChestSortBaseScreen):
    """
    ChestSort
    """

    def __init__(self, namespace, name):
        ChestSortBaseScreen.__init__(self, namespace, name)
        print '==== %s ====' % 'init LargeChestScreen'
        self.bindParent = "variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel/root_panel/chest_panel/large_chest_panel_top_half/chest_label"

    def OnCreate(self):
        ChestSortBaseScreen.OnCreate(self)
        print '==== %s ====' % 'LargeChestScreen Create'
        self.LoadSortButton()

    def RequestSort(self):
        self.clientSystem.RequestSort("chest")

    def LoadSortButton(self):
        parentControl = self.screen.GetBaseUIControl(self.bindParent)
        self.screen.CreateChildControl("sort_button.sort_button", "sort_button", parentControl)
