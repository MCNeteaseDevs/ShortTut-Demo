# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi

from demoMinimapScript.ui.uiDef import UIDef

ScreenNode = clientApi.GetScreenNodeCls()
MiniMapBaseScreen = clientApi.GetMiniMapScreenNodeCls()
ViewBinder = clientApi.GetViewBinderCls()


class MinimapScreen(MiniMapBaseScreen):
    """
    Minimap
    """

    def __init__(self, namespace, name, param):
        MiniMapBaseScreen.__init__(self, namespace, name, param)
        # param 为PushScreen中传来的Dict
        print '==== %s ====' % 'init MinimapScreen'
        self.minimapPath = "/variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel/image/panel/mini_map_wrapper(0)/netease_mini_map"

    @ViewBinder.binding(ViewBinder.BF_ButtonClickUp)
    def OnPlusClick(self, args):
        control = self.GetBaseUIControl(self.minimapPath).asMiniMap()
        control.ZoomIn()

    @ViewBinder.binding(ViewBinder.BF_ButtonClickUp)
    def OnMinusClick(self, args):
        control = self.GetBaseUIControl(self.minimapPath).asMiniMap()
        control.ZoomOut()

    @ViewBinder.binding(ViewBinder.BF_BindString, "#position")
    def OnReturnPosition(self):
        posComp = clientApi.GetEngineCompFactory().CreatePos(clientApi.GetLocalPlayerId())
        pos = posComp.GetFootPos()
        return "{:.1f},{:.1f},{:.1f}".format(*pos)
