# -*- coding: utf-8 -*-
import mod.client.extraClientApi as extraClientApi
import demoLaserScript.ui.uiDef as uiDef
from demoLaserScript.laserConst import ModName


class UIMgr(object):
    def __init__(self):
        super(UIMgr, self).__init__()
        self.mUIDict = {}
        self.mClientSystem = None

    def Destroy(self):
        pass

    def Init(self, system):
        self.mClientSystem = system
        for uiKey, config in uiDef.UIData.iteritems():
            self.InitSingleUI(uiKey, config)

    def InitSingleUI(self, uiKey, config):
        cls, screen = config["cls"], config["screen"]
        extraClientApi.RegisterUI(ModName, uiKey, cls, screen)
        if config.get("version", 1) == 1:
            extraParam = {}
            if config.has_key("isHud"):
                extraParam["isHud"] = config["isHud"]
            ui = extraClientApi.CreateUI(ModName, uiKey, extraParam)
            if not ui:
                print "InitSingleUI %s fail" % uiKey
                return
            if config.has_key("layer"):
                ui.GetBaseUIControl("").SetLayer(config["layer"])
            self.mUIDict[uiKey] = ui

    def PushScreen(self, uiKey, params=None):
        return extraClientApi.PushScreen(ModName, uiKey, params)

    def GetUI(self, uiKey):
        return self.mUIDict.get(uiKey, None)

    def RemoveUI(self, uiKey):
        ui = self.mUIDict.get(uiKey, None)
        if ui:
            del self.mUIDict[uiKey]
            ui.SetRemove()
            return True
        return False
