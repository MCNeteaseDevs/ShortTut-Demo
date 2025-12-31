# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi

ScreenNode = clientApi.GetScreenNodeCls()


class UncraftingScreen(ScreenNode):
    """
    Uncrafting
    """

    def __init__(self, namespace, name, param):
        ScreenNode.__init__(self, namespace, name, param)
        # param 为PushScreen中传来的Dict
        print '==== %s ====' % 'init UncraftingScreen'

    # Create函数是继承自ScreenNode，会在UI创建完成后被调用
    def Create(self):
        print '==== %s ====' % 'UncraftingScreen Create'

    # 调用该函数可以关闭UI界面
    def Close(self):
        clientApi.PopScreen()
