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
HINT_LABEL_PATH = "/center_panel/hint_label"

# 演示数据：40 条，足够超出可视区域
ITEM_NAMES = [
    "钻石剑", "苹果", "铁镐", "面包", "火把", "箭", "木棍", "煤炭",
    "铁锭", "金锭", "绿宝石", "指南针", "时钟", "地图", "书", "骨头",
    "线", "羽毛", "火药", "小麦", "胡萝卜", "马铃薯", "牛肉", "皮革",
    "甘蔗", "南瓜", "西瓜", "蛋糕", "曲奇", "蜂蜜瓶", "鸡蛋", "牛奶",
    "熟鱼", "生鱼", "红石", "青金石", "石英", "下界合金", "末影珍珠", "潜影壳"
]

# 按 4 键依次跳到的条目下标，用来演示 SetScrollViewPos(下标 × 行高)
# 内容总高 40 × 20 = 800，窗口 120，能滚的范围是 0~680，所以取的下标都留在范围内
LOCATE_TARGETS = [6, 19, 26]


class ScrollUIScreen(ScreenNode):
    """
    滚动列表演示

    - 界面上没有控制按钮，滚动只由快捷键（客户端 System 转发进来）驱动
    - 列表数据靠 ViewBinder 的集合绑定填进去，不用一个个控件去改
    - 条目数量交给 "#grid.size"，JSON 里 grid 再把它转成 #maximum_grid_items
    """

    def __init__(self, namespace, name, param):
        ScreenNode.__init__(self, namespace, name, param)
        self.mRows = []
        for index, name in enumerate(ITEM_NAMES):
            self.mRows.append("%02d  %s" % (index + 1, name))
        self.mScrollView = None
        self.mPercent = -1
        self.mTick = 0
        self.mLocateIndex = -1

    # ---------- 生命周期 ----------

    def Create(self):
        self.mScrollView = self._GetScrollView()
        if not self.mScrollView:
            logger.info("ScrollUIScreen scroll_view not found at %s", SCROLL_VIEW_PATH)
        self._RefreshPercentLabel(0)
        self._SetLabelText(HINT_LABEL_PATH, "1顶部 2底部 3下10％ 4定位 5读取 6内容")

    def Update(self):
        # 每 6 帧（约 0.2 秒）读一次百分比，滚轮 / 拖滚动条时下面那行也能跟上
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
        return self.mRows[index]

    # ---------- 给快捷键调的入口 ----------

    def SetPercent(self, percent):
        """SetScrollViewPercentValue：按百分比跳，0 顶部、100 底部"""
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
        self._SetLabelText(
            HINT_LABEL_PATH,
            "SetScrollViewPercentValue(%d)" % percent
        )

    def StepPercent(self, delta):
        """先 Get 再 Set：读当前百分比，加减后再写回去"""
        percent = self._GetPercent()
        if percent < 0:
            return
        target = percent + delta
        if target < 0:
            target = 0
        elif target > 100:
            target = 100
        self.SetPercent(target)
        self._SetLabelText(
            HINT_LABEL_PATH,
            "Get:%d Set:%d" % (percent, target)
        )

    def LocateSelected(self):
        """SetScrollViewPos：像素定位，把第 N 条顶到最上面"""
        self.mLocateIndex = (self.mLocateIndex + 1) % len(LOCATE_TARGETS)
        index = LOCATE_TARGETS[self.mLocateIndex]
        scrollView = self._GetScrollView()
        if not scrollView:
            return
        pos = index * ROW_HEIGHT
        scrollView.SetScrollViewPos(pos)
        self.mPercent = -1
        self._SetLabelText(
            HINT_LABEL_PATH,
            "SetScrollViewPos(%d x %d = %d)" % (index, ROW_HEIGHT, pos)
        )

    def ReadPos(self):
        """GetScrollViewPercentValue + GetScrollViewPos"""
        scrollView = self._GetScrollView()
        if not scrollView:
            return
        percent = int(scrollView.GetScrollViewPercentValue())
        pos = scrollView.GetScrollViewPos()
        self._RefreshPercentLabel(percent)
        self._SetLabelText(
            HINT_LABEL_PATH,
            "Percent:%d Pos:%d" % (percent, int(pos))
        )

    def ReadContentPath(self):
        """GetScrollViewContentPath + GetScrollViewContentControl"""
        scrollView = self._GetScrollView()
        if not scrollView:
            return
        path = scrollView.GetScrollViewContentPath()
        control = scrollView.GetScrollViewContentControl()
        if path:
            # 完整路径太长会顶出面板，只留最后一段
            path = path.rsplit("/", 1)[-1]
        self._SetLabelText(
            HINT_LABEL_PATH,
            "Content:%s %s" % (
                path if path else "None",
                "OK" if control else "None"
            )
        )

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

    def _RefreshPercentLabel(self, percent):
        scrollView = self._GetScrollView()
        pos = int(scrollView.GetScrollViewPos()) if scrollView else 0
        self._SetLabelText(
            PERCENT_LABEL_PATH,
            "滚动位置 %d%%  像素 %d" % (percent, pos)
        )

    def _SetLabelText(self, path, text):
        control = self.GetBaseUIControl(path)
        if not control:
            return
        label = control.asLabel()
        if label:
            label.SetText(text)
