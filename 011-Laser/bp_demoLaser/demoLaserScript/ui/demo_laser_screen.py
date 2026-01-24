# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi

ScreenNode = clientApi.GetScreenNodeCls()


class LaserScreen(ScreenNode):
    """
    Laser
    """

    def __init__(self, namespace, name, param):
        ScreenNode.__init__(self, namespace, name, param)
        # param 为PushScreen中传来的Dict
        print '==== %s ====' % 'init LaserScreen'

    # Create函数是继承自ScreenNode，会在UI创建完成后被调用
    def Create(self):
        print '==== %s ====' % 'LaserScreen Create'

    # 调用该函数可以关闭UI界面
    def Close(self):
        clientApi.PopScreen()
