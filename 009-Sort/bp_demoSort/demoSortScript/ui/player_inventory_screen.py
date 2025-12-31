# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi

from demoSortScript.ui.chest_sort_base_screen import ChestSortBaseScreen

ScreenNode = clientApi.GetScreenNodeCls()
CustomUIScreenProxy = clientApi.GetUIScreenProxyCls()
ViewBinder = clientApi.GetViewBinderCls()


class PlayerInventoryScreen(ChestSortBaseScreen):
    """
    PlayerInventoryScreen
    """

    def __init__(self, namespace, name):
        ChestSortBaseScreen.__init__(self, namespace, name)
        print '==== %s ====' % 'init PlayerInventoryScreen'

    def OnCreate(self):
        ChestSortBaseScreen.OnCreate(self)
        print '==== %s ====' % 'PlayerInventoryScreen Create'
        self.LoadSortButton()

    def RequestSort(self):
        self.clientSystem.RequestSort("inv")

    def LoadSortButton(self):
        parentControl = self.screen.GetBaseUIControl("/variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel/content_stack_panel/player_inventory/inventory_panel_top_half")
        self.screen.CreateChildControl("sort_button.sort_button_left_bottom", "sort_button_left_bottom", parentControl)
