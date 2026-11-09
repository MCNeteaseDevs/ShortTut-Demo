# -*- coding: utf-8 -*-

from mod.common.mod import Mod
import mod.client.extraClientApi as clientApi
import mod.server.extraServerApi as serverApi
from mod_log import logger

import compoundBowScript.compoundBowConst as conf


@Mod.Binding(name=conf.ModName, version=conf.ModVersion)
class CompoundBowMod(object):
    @Mod.InitClient()
    def OnClientInit(self):
        logger.info("%s initClient", conf.ModName)
        clientApi.RegisterSystem(
            conf.ModName,
            conf.ClientSystemName,
            conf.ClientSystemClsPath
        )

    @Mod.DestroyClient()
    def OnClientDestroy(self):
        logger.info("%s destroyClient", conf.ModName)

    @Mod.InitServer()
    def OnServerInit(self):
        logger.info("%s initServer", conf.ModName)
        serverApi.RegisterSystem(
            conf.ModName,
            conf.ServerSystemName,
            conf.ServerSystemClsPath
        )

    @Mod.DestroyServer()
    def OnServerDestroy(self):
        logger.info("%s destroyServer", conf.ModName)
