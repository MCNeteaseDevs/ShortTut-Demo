# -*- coding: utf-8 -*-

from mod.common.mod import Mod
import mod.client.extraClientApi as clientApi
import mod.server.extraServerApi as serverApi
from demoUncraftingScript.uncraftingConst import ModVersion, ModName, ClientSystemName, ClientSystemClsPath, ServerSystemName, ServerSystemClsPath
from mod_log import logger


@Mod.Binding(name=ModName, version=ModVersion)
class NeteaseUncraftingClient(object):
    @Mod.InitClient()
    def UncraftingClientInit(self):
        logger.info("%s initClient", ModName)
        clientApi.RegisterSystem(ModName, ClientSystemName, ClientSystemClsPath)

    @Mod.DestroyClient()
    def UncraftingClientDestroy(self):
        logger.info("%s destroyClient", ModName)

    @Mod.InitServer()
    def UncraftingServerInit(self):
        logger.info("%s initServer", ModName)
        serverApi.RegisterSystem(ModName, ServerSystemName, ServerSystemClsPath)

    @Mod.DestroyServer()
    def UncraftingServerDestroy(self):
        logger.info("%s destroyServer", ModName)
