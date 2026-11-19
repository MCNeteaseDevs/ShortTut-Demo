# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi
from mod_log import logger

ScreenNode = clientApi.GetScreenNodeCls()
ViewBinder = clientApi.GetViewBinderCls()

# 列表里每条的高度，要和模板 row_template 的高度保持一致（定位时按这个换算像素）
ROW_HEIGHT = 20
# 编辑器里拖进去的 scroll_view 控件名
SCROLL_VIEW_PATH = "/center_panel/scroll_list"
PERCENT_LABEL_PATH = "/center_panel/percent_label"
DETAIL_LABEL_PATH = "/center_panel/detail_label"

# 演示数据：40 条，足够超出可视区域
ITEM_NAMES = [
    u"钻石剑", u"苹果", u"铁镐", u"面包", u"火把", u"箭", u"木棍", u"煤炭",
    u"铁锭", u"金锭", u"绿宝石", u"指南针", u"时钟", u"地图", u"书", u"骨头",
    u"线", u"羽毛", u"火药", u"小麦", u"胡萝卜", u"马铃薯", u"牛肉", u"皮革",
    u"甘蔗", u"南瓜", u"西瓜", u"蛋糕", u"曲奇", u"蜂蜜瓶", u"鸡蛋", u"牛奶",
    u"熟鱼", u"生鱼", u"红石", u"青金石", u"石英", u"下界合金", u"末影珍珠", u"潜影壳"
]


class ScrollUIScreen(ScreenNode):
    """
    滚动列表演示

    - 列表数据靠 ViewBinder 的集合绑定填进去，不用一个个控件去改
    - 条目数量交给 "#grid.size"，JSON 里 grid 再把它转成 #maximum_grid_items
    - 滚动位置用 ScrollViewUIControl 的百分比 / 像素接口
    """

    def __init__(self, namespace, name, param):
        ScreenNode.__init__(self, namespace, name, param)
        self.mRows = []
        for index, name in enumerate(ITEM_NAMES):
            self.mRows.append(u"%02d  %s" % (index + 1, name))
        self.mSelected = -1
        self.mScrollView = None
        self.mPercent = -1
        self.mTick = 0

    # ---------- 生命周期 ----------

    def Create(self):
        # 缓存 ScrollViewUIControl，后面的滚动都靠它
        self.mScrollView = self._GetScrollView()
        if not self.mScrollView:
            logger.info("ScrollUIScreen scroll_view not found at %s", SCROLL_VIEW_PATH)
        self._SetLabelText(PERCENT_LABEL_PATH, u"滚动位置 0％")
        self._SetLabelText(DETAIL_LABEL_PATH, u"点一下列表里的条目")

    def Update(self):
        # 每 6 帧（约 0.2 秒）读一次百分比，这样拖动滚动条时标签也能跟上
        self.mTick += 1
        if self.mTick % 6 != 0:
            return
        percent = self._GetPercent()
        if percent < 0 or percent == self.mPercent:
            return
        self.mPercent = percent
        self._RefreshPercentLabel(percent)

    # ---------- 数据绑定 ----------

    @ViewBinder.binding(ViewBinder.BF_BindInt, "#grid.size")
    def OnBindGridSize(self):
        # JSON 里 grid 的 #maximum_grid_items 绑的就是这个值
        return len(self.mRows)

    @ViewBinder.binding_collection(ViewBinder.BF_BindString, "row_grid", "#row.title")
    def OnBindRowText(self, index):
        if index < 0 or index >= len(self.mRows):
            return ""
        # 注意：集合绑定要返回 str，直接返回 unicode 的话文字不会显示
        return self.mRows[index].encode("utf-8")

    # ---------- 列表条目 ----------

    @ViewBinder.binding(ViewBinder.BF_ButtonClickUp)
    def OnRowClick(self, args):
        index = args.get("#collection_index", -1)
        if not isinstance(index, int):
            try:
                index = int(index)
            except (TypeError, ValueError):
                return
        if index < 0 or index >= len(self.mRows):
            return
        self.mSelected = index
        self._SetLabelText(
            DETAIL_LABEL_PATH,
            u"已选 第 %02d 条：%s" % (index + 1, ITEM_NAMES[index])
        )

    # ---------- 滚动按钮 ----------

    @ViewBinder.binding(ViewBinder.BF_ButtonClickUp)
    def OnTopClick(self, args):
        self._SetPercent(0)

    @ViewBinder.binding(ViewBinder.BF_ButtonClickUp)
    def OnUpClick(self, args):
        self._SetPercent(self._GetPercent() - 10)

    @ViewBinder.binding(ViewBinder.BF_ButtonClickUp)
    def OnDownClick(self, args):
        self._SetPercent(self._GetPercent() + 10)

    @ViewBinder.binding(ViewBinder.BF_ButtonClickUp)
    def OnBottomClick(self, args):
        self._SetPercent(100)

    @ViewBinder.binding(ViewBinder.BF_ButtonClickUp)
    def OnLocateClick(self, args):
        if self.mSelected < 0:
            self._SetLabelText(DETAIL_LABEL_PATH, u"先点一条，再定位")
            return
        scrollView = self._GetScrollView()
        if not scrollView:
            return
        # 像素接口：把这一条的顶部滚到窗口最上面
        scrollView.SetScrollViewPos(self.mSelected * ROW_HEIGHT)
        self._SetLabelText(DETAIL_LABEL_PATH, u"已定位 第 %02d 条" % (self.mSelected + 1))

    @ViewBinder.binding(ViewBinder.BF_ButtonClickUp)
    def OnCloseClick(self, args):
        self.Close()

    # ---------- 滚动控件 ----------

    def _GetScrollView(self):
        if self.mScrollView:
            return self.mScrollView
        control = self.GetBaseUIControl(SCROLL_VIEW_PATH)
        if not control:
            return None
        scrollView = control.asScrollView()
        if scrollView:
            self.mScrollView = scrollView
        return scrollView

    def _GetPercent(self):
        scrollView = self._GetScrollView()
        if not scrollView:
            return -1
        return int(scrollView.GetScrollViewPercentValue())

    def _SetPercent(self, percent):
        if percent < 0:
            percent = 0
        elif percent > 100:
            percent = 100
        scrollView = self._GetScrollView()
        if not scrollView:
            return
        scrollView.SetScrollViewPercentValue(percent)
        self.mPercent = percent
        self._RefreshPercentLabel(percent)

    def _RefreshPercentLabel(self, percent):
        self._SetLabelText(PERCENT_LABEL_PATH, u"滚动位置 %d％" % percent)

    def _SetLabelText(self, path, text):
        control = self.GetBaseUIControl(path)
        if not control:
            return
        label = control.asLabel()
        if label:
            label.SetText(text)

    # 调用该函数可以关闭UI界面
    def Close(self):
        clientApi.PopScreen()
