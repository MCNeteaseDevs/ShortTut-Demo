# -*- coding: utf-8 -*-

from mod.common.mod import Mod
import mod.client.extraClientApi as clientApi
import mod.server.extraServerApi as serverApi
from demoPlayerModelScript.playerModelConst import ModVersion, ModName, ClientSystemName, ClientSystemClsPath, ServerSystemName, ServerSystemClsPath
from mod_log import logger


@Mod.Binding(name=ModName, version=ModVersion)
class NeteasePlayerModelClient(object):
    @Mod.InitClient()
    def PlayerModelClientInit(self):
        logger.info("%s initClient", ModName)
        clientApi.RegisterSystem(ModName, ClientSystemName, ClientSystemClsPath)

    @Mod.DestroyClient()
    def PlayerModelClientDestroy(self):
        logger.info("%s destroyClient", ModName)

    @Mod.InitServer()
    def PlayerModelServerInit(self):
        logger.info("%s initServer", ModName)
        serverApi.RegisterSystem(ModName, ServerSystemName, ServerSystemClsPath)

    @Mod.DestroyServer()
    def PlayerModelServerDestroy(self):
        logger.info("%s destroyServer", ModName)
