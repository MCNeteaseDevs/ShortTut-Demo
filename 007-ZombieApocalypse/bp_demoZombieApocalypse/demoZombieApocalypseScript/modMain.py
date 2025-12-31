# -*- coding: utf-8 -*-

from mod.common.mod import Mod
import mod.client.extraClientApi as clientApi
import mod.server.extraServerApi as serverApi
from demoZombieApocalypseScript.zombieApocalypseConst import ModVersion, ModName, ClientSystemName, ClientSystemClsPath, ServerSystemName, ServerSystemClsPath
from mod_log import logger


@Mod.Binding(name=ModName, version=ModVersion)
class NeteaseZombieApocalypseClient(object):
    @Mod.InitClient()
    def ZombieApocalypseClientInit(self):
        logger.info("%s initClient", ModName)
        clientApi.RegisterSystem(ModName, ClientSystemName, ClientSystemClsPath)

    @Mod.DestroyClient()
    def ZombieApocalypseClientDestroy(self):
        logger.info("%s destroyClient", ModName)

    @Mod.InitServer()
    def ZombieApocalypseServerInit(self):
        logger.info("%s initServer", ModName)
        serverApi.RegisterSystem(ModName, ServerSystemName, ServerSystemClsPath)

    @Mod.DestroyServer()
    def ZombieApocalypseServerDestroy(self):
        logger.info("%s destroyServer", ModName)
