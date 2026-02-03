# -*- coding: utf-8 -*-

from mod.common.mod import Mod


@Mod.Binding(name="Script_NeteaseModhwhvbC2v", version="0.0.1")
class Script_NeteaseModhwhvbC2v(object):

    def __init__(self):
        pass

    @Mod.InitServer()
    def Script_NeteaseModhwhvbC2vServerInit(self):
        pass

    @Mod.DestroyServer()
    def Script_NeteaseModhwhvbC2vServerDestroy(self):
        pass

    @Mod.InitClient()
    def Script_NeteaseModhwhvbC2vClientInit(self):
        pass

    @Mod.DestroyClient()
    def Script_NeteaseModhwhvbC2vClientDestroy(self):
        pass
