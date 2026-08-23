# -*- coding: utf-8 -*-

from mod.common.mod import Mod
import mod.client.extraClientApi as clientApi
import mod.server.extraServerApi as serverApi

from Script_NeteaseModhwhvbC2v.chairConst import (
    ClientSystemClsPath,
    ClientSystemName,
    ModName,
    ModVersion,
    ServerSystemClsPath,
    ServerSystemName
)


@Mod.Binding(name=ModName, version=ModVersion)
class Script_NeteaseModhwhvbC2v(object):

    def __init__(self):
        pass

    @Mod.InitServer()
    def Script_NeteaseModhwhvbC2vServerInit(self):
        serverApi.RegisterSystem(ModName, ServerSystemName, ServerSystemClsPath)

    @Mod.DestroyServer()
    def Script_NeteaseModhwhvbC2vServerDestroy(self):
        pass

    @Mod.InitClient()
    def Script_NeteaseModhwhvbC2vClientInit(self):
        clientApi.RegisterSystem(ModName, ClientSystemName, ClientSystemClsPath)

    @Mod.DestroyClient()
    def Script_NeteaseModhwhvbC2vClientDestroy(self):
        pass
