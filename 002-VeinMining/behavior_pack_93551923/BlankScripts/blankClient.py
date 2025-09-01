# -*- coding: utf-8 -*-
#
import mod.client.extraClientApi as clientApi


class BlankClient(clientApi.GetClientSystemCls()):
    def __init__(self, namespace, name):
        super(BlankClient, self).__init__(namespace, name)
        self.ListenEvent()
        self.levelId = clientApi.GetLevelId()

    # 在类初始化的时候开始监听
    def ListenEvent(self):
        self.ListenForEvent(clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(),
                            'LoadClientAddonScriptsAfter',
                            self, self.OnLoadClientAddon)

    # 取消监听
    def UnListenEvent(self):
        self.UnListenForEvent(clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(),
                              "LoadClientAddonScriptsAfter",
                              self, self.OnLoadClientAddon)

    # 在Destroy中调用反注册取消监听
    def Destroy(self):
        self.UnListenEvent()
        print('====客户端完成反注册====')

    def OnLoadClientAddon(self, data):
        print('====客户端加载mod完成事件====')
