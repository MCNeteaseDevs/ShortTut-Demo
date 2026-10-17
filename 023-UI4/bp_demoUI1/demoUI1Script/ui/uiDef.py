# -*- coding: utf-8 -*-
import mod.client.extraClientApi as extraClientApi


class UIDef:
    UI1Screen = "UI1Screen"
    EasingCompare = "EasingCompare"


UIData = {
    UIDef.UI1Screen: {
        "cls": "demoUI1Script.ui.backpack.BackpackScreen",
        "screen": "backpack.main",
        "version": 2
    },
    UIDef.EasingCompare: {
        "cls": "demoUI1Script.ui.easingCompareScreen.EasingCompareScreen",
        "screen": "easing_compare.main",
        "version": 2
    }
}
