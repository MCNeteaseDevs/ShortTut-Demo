# coding=utf-8
import copy

from demoSortScript import hash_dict
import mod.server.extraServerApi as serverApi


class Sortable:

    def __init__(self):
        self.itemComp = serverApi.GetEngineCompFactory().CreateItem(serverApi.GetLevelId())
        self.blockInfoComp = serverApi.GetEngineCompFactory().CreateBlockInfo(serverApi.GetLevelId())
        pass

    def Update(self, args):
        pass

    def GetSize(self):
        return 0

    def GetStart(self):
        return 0

    def GetContainerItem(self, index):
        return {}

    def SetContainerItem(self, index, item):
        pass

    def DoSort(self):
        chestSize = self.GetSize()
        if chestSize == -1:
            return False
        start = self.GetStart()
        nonNullItemDicts = []
        for i in xrange(start, chestSize):
            itemDict = self.GetContainerItem(i)
            if not itemDict:
                continue
            nonNullItemDicts.append(itemDict)
        result = self.AutoMerge(nonNullItemDicts)  # 先合并一次
        result.sort(key=lambda item: item["newItemName"])  # 在排序
        for i in xrange(start, chestSize):  # 先清空
            self.SetContainerItem(i, {})
        # 东西放回去
        for i, item in enumerate(result):
            self.SetContainerItem(start + i, item)

    def AutoMerge(self, items):
        hashToAmount = {}
        hashToItem = {}
        # 先计数每个物品各有多少个
        for item in items:
            item_copy = copy.copy(item)
            del item_copy["count"]
            itemHash = hash_dict(item_copy)
            hashToItem[itemHash] = item
            hashToAmount[itemHash] = hashToAmount.get(itemHash, 0) + item["count"]
        # 再计算物品有哪些是能合并
        result = []
        for itemHash, amount in hashToAmount.items():
            item = hashToItem[itemHash]
            basicInfo = self.itemComp.GetItemBasicInfo(item["newItemName"], item["newAuxValue"])
            maxStack = basicInfo["maxStackSize"]
            if amount <= maxStack:
                # 不需要合并
                # print "不合并", item["newItemName"], amount
                item["count"] = amount
                result.append(item)
            else:
                # 合并
                stackCount = amount // maxStack  # 会有几个stack
                stackMod = amount % maxStack  # 几个stack零几个item
                # print "合并", item["newItemName"], amount, ":", stackCount, "+", stackMod

                for i in xrange(stackCount):
                    mergeItem = copy.copy(item)
                    mergeItem["count"] = maxStack
                    result.append(mergeItem)
                if stackMod:
                    mergeItem = copy.copy(item)
                    mergeItem["count"] = stackMod
                    result.append(mergeItem)
        return result
