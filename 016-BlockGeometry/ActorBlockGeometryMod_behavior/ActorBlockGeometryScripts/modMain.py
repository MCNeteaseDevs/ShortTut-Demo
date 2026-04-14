# -*- coding: utf-8 -*-

from common.mod import Mod
import mod.client.extraClientApi as clientApi
import mod.server.extraServerApi as serverApi
from modCommon import modConfig

@Mod.Binding(name="ActorBlockGeometryMod", version="0.0.1")
class NeteaseModVf4JPaVx(object):

    def __init__(self):
        pass

    @Mod.InitServer()
    def ActorBlockGeometryModServerInit(self):
        serverApi.RegisterSystem(modConfig.modName, modConfig.modServerSystem, modConfig.modServerSystemCls)

    @Mod.DestroyServer()
    def ActorBlockGeometryModServerDestroy(self):
        pass

    @Mod.InitClient()
    def ActorBlockGeometryModClientInit(self):
        clientApi.RegisterSystem(modConfig.modName, modConfig.modClientSystem, modConfig.modClientSystemCls)

    @Mod.DestroyClient()
    def ActorBlockGeometryModClientDestroy(self):
        pass
