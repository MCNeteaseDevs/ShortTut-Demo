# -*- coding: utf-8 -*-

from mod.common.mod import Mod
import mod.client.extraClientApi as clientApi
import mod.server.extraServerApi as serverApi
from demoPlayerLootScript.playerLootConst import ModVersion, ModName, ClientSystemName, ClientSystemClsPath, ServerSystemName, ServerSystemClsPath
from mod_log import logger


@Mod.Binding(name=ModName, version=ModVersion)
class NeteasePlayerLootClient(object):
    @Mod.InitClient()
    def PlayerLootClientInit(self):
        logger.info("%s initClient", ModName)
        clientApi.RegisterSystem(ModName, ClientSystemName, ClientSystemClsPath)

    @Mod.DestroyClient()
    def PlayerLootClientDestroy(self):
        logger.info("%s destroyClient", ModName)

    @Mod.InitServer()
    def PlayerLootServerInit(self):
        logger.info("%s initServer", ModName)
        serverApi.RegisterSystem(ModName, ServerSystemName, ServerSystemClsPath)

    @Mod.DestroyServer()
    def PlayerLootServerDestroy(self):
        logger.info("%s destroyServer", ModName)
