# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi

ScreenNode = clientApi.GetScreenNodeCls()
ViewBinder = clientApi.GetViewBinderCls()
ViewRequest = clientApi.GetViewViewRequestCls()

GRID_COLUMN = 9
GRID_ROW = 4
SLOT_COUNT = GRID_COLUMN * GRID_ROW

# 模拟背包数据：格子下标 -> (物品名, 数量)，没有列出的格子视为空格子
MOCK_ITEMS = {
    0: ("minecraft:diamond", 5),
    1: ("minecraft:apple", 12),
    3: ("minecraft:iron_sword", 1),
    4: ("minecraft:bread", 32),
    5: ("minecraft:oak_planks", 64),
    8: ("minecraft:bow", 1),
    9: ("minecraft:golden_apple", 3),
    12: ("minecraft:tnt", 16),
    13: ("minecraft:ender_pearl", 2),
    18: ("minecraft:cake", 1),
    20: ("minecraft:emerald", 27),
    22: ("minecraft:compass", 1),
    27: ("minecraft:iron_ingot", 45),
    31: ("minecraft:cooked_beef", 8),
}


class BackpackScreen(ScreenNode):
    """模拟背包界面：演示 grid + binding_collection 集合绑定"""

    def __init__(self, namespace, name, param):
        ScreenNode.__init__(self, namespace, name, param)
        self.selected = -1
        # 三个与格子一一对应的列表，列表下标就是格子的 index
        self.slots = [None] * SLOT_COUNT
        self.slotIdAuxList = [0] * SLOT_COUNT
        self.slotNameList = [""] * SLOT_COUNT
        self._InitMockData()

    def _InitMockData(self):
        # 初始化时提前查好 id_aux 和显示名并缓存，
        # 避免在高频调用的绑定函数里做查询
        itemComp = clientApi.GetEngineCompFactory().CreateItem(clientApi.GetLevelId())
        for index, itemTuple in MOCK_ITEMS.iteritems():
            if index >= SLOT_COUNT:
                continue
            itemName, count = itemTuple
            info = itemComp.GetItemBasicInfo(itemName, 0)
            if not info:
                continue
            self.slots[index] = {"name": itemName, "count": count}
            self.slotIdAuxList[index] = info["id_aux"]
            self.slotNameList[index] = info["itemName"]

    # ---------- 集合绑定：一个函数给所有格子供数据 ----------

    @ViewBinder.binding_collection(ViewBinder.BF_BindInt, "backpack_grid", "#slot.item")
    def GetSlotItem(self, index):
        # 返回 id_aux，物品渲染控件根据它渲染对应物品
        return self.slotIdAuxList[index]

    @ViewBinder.binding_collection(ViewBinder.BF_BindString, "backpack_grid", "#slot.amount")
    def GetSlotAmount(self, index):
        # 数量小于等于 1 时不显示数字，和原版背包保持一致
        item = self.slots[index]
        if not item or item["count"] <= 1:
            return ""
        return str(item["count"])

    @ViewBinder.binding_collection(ViewBinder.BF_BindBool, "backpack_grid", "#slot.selected")
    def GetSlotSelected(self, index):
        # 只有当前选中的格子返回 True，高亮框才会显示
        return index == self.selected

    # ---------- 全局绑定 ----------

    @ViewBinder.binding(ViewBinder.BF_BindString, "#detail_text")
    def GetDetailText(self):
        if self.selected < 0 or not self.slots[self.selected]:
            return "点击格子查看物品"
        item = self.slots[self.selected]
        return "{} x{}".format(self.slotNameList[self.selected], item["count"])

    # ---------- 按钮事件 ----------

    @ViewBinder.binding(ViewBinder.BF_ButtonClickUp)
    def on_slot_click(self, args):
        # 绑定名使用 %backpack.on_slot_click，所以这里不写绑定名，函数名保持一致
        # 配置了 collection_details 的按钮，参数里会带上被点击格子的下标
        index = args.get("#collection_index", -1)
        if 0 <= index < SLOT_COUNT and self.slots[index]:
            self.selected = index
        return ViewRequest.Refresh

    @ViewBinder.binding(ViewBinder.BF_ButtonClickUp, "#close_backpack")
    def CloseBackpack(self, args):
        clientApi.PopScreen()
