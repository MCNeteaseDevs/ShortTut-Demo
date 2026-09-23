# -*- coding: utf-8 -*-

import mod.server.extraServerApi as serverApi

ServerSystem = serverApi.GetServerSystemCls()


class CameraServerSystem(ServerSystem):
    def __init__(self, namespace, systemName):
        ServerSystem.__init__(self, namespace, systemName)
