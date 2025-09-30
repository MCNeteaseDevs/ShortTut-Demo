# -*- coding: utf-8 -*-

import mod.client.extraClientApi as clientApi
import demoSweepingScript.sweepingConst as SweepingConst
from mod_log import logger

ClientSystem = clientApi.GetClientSystemCls()


class SweepingClientSystem(ClientSystem):
    """
    该mod的客户端类
    根据服务端推送下来的数据显示通用显示界面
    """

    def __init__(self, namespace, systemName):
        ClientSystem.__init__(self, namespace, systemName)

    def Destroy(self):

        pass
