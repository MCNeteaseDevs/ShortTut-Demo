# -*- coding: utf-8 -*-
import mod.client.extraClientApi as extraClientApi


class UIDef:
    DemoMinimap = "DemoMinimap"


UIData = {
    UIDef.DemoMinimap: {
        "cls": "demoMinimapScript.ui.demo_minimap_screen.MinimapScreen",
        "screen": "demo_minimap.main",
        "version": 1,
        "isHud": 1,
        "extraParam": {
            "mini_map_root_path": "/variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel/image/panel/mini_map_wrapper(0)"
        }
    }
}
