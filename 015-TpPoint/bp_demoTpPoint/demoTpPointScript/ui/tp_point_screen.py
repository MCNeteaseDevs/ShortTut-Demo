# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi
from demoTpPointScript.tpPointConst import ModName, ClientSystemName, ServerSystemName, SyncTpPointsEvent

ScreenNode = clientApi.GetScreenNodeCls()
ViewBinder = clientApi.GetViewBinderCls()
ViewRequest = clientApi.GetViewViewRequestCls()


class TpPointScreen(ScreenNode):
    """
    TpPoint
    """

    def __init__(self, namespace, name, param):
        ScreenNode.__init__(self, namespace, name, param)
        # param 为PushScreen中传来的Dict
        print '==== %s ====' % 'init TpPointScreen'
        self.mNameInput = ""
        self.mPoints = param.get("points", []) if param else []
        self.mClientSystem = None

    @ViewBinder.binding(ViewBinder.BF_BindInt, "#grid.size")
    def OnBindGridSize(self):
        return len(self.mPoints)

    @ViewBinder.binding_collection(ViewBinder.BF_BindString, "point_grid", "#point.name")
    def OnBindPointName(self, index):
        return self.mPoints[index]["name"]

    @ViewBinder.binding(ViewBinder.BF_BindString, "#input")
    def OnReturnNameInput(self):
        return self.mNameInput

    @ViewBinder.binding(ViewBinder.BF_EditFinished)
    def OnNameInputFinish(self, args):
        text = args["Text"]
        self.mNameInput = text
        return ViewRequest.Refresh

    @ViewBinder.binding(ViewBinder.BF_ButtonClickUp)
    def OnAddClick(self, args):
        name = self.mNameInput.strip()
        if not name:
            return
        self.mClientSystem.RequestAddTpPoint(name)
        self.mNameInput = ""
        return ViewRequest.Refresh

    # Create函数是继承自ScreenNode，会在UI创建完成后被调用
    def Create(self):
        print '==== %s ====' % 'TpPointScreen Create'
        self.mClientSystem = clientApi.GetSystem(ModName, ClientSystemName)
        # 监听服务端同步传送点事件
        self.mClientSystem.ListenForEvent(
            ModName, ServerSystemName,
            SyncTpPointsEvent, self, self.OnSyncTpPoints
        )

    # 调用该函数可以关闭UI界面
    def Close(self):
        # 取消监听
        if self.mClientSystem:
            self.mClientSystem.UnListenForEvent(
                ModName, ServerSystemName,
                SyncTpPointsEvent, self, self.OnSyncTpPoints
            )
        clientApi.PopScreen()

    @ViewBinder.binding(ViewBinder.BF_ButtonClickUp)
    def OnCloseClick(self, args):
        self.Close()

    def OnSyncTpPoints(self, args):
        """服务端同步传送点列表（增删后刷新）"""
        points = args.get("points", [])
        self.UpdatePoints(points)

    def UpdatePoints(self, points):
        """由客户端系统调用，刷新传送点数据"""
        self.mPoints = points
        self.UpdateScreen()

    @ViewBinder.binding(ViewBinder.BF_ButtonClickUp)
    def OnTpClick(self, args):
        index = args["#collection_index"]
        pointName = self.mPoints[index]["name"]
        self.DoTeleport(pointName)

    @ViewBinder.binding(ViewBinder.BF_ButtonClickUp)
    def OnDeleteClick(self, args):
        index = args["#collection_index"]
        pointName = self.mPoints[index]["name"]
        self.DoDelete(pointName)

    # ---- 供外部/子类调用的传送与删除方法 ----

    def DoTeleport(self, pointName):
        self.mClientSystem.RequestTeleport(pointName)
        self.Close()

    def DoDelete(self, pointName):
        self.mClientSystem.RequestDeleteTpPoint(pointName)
