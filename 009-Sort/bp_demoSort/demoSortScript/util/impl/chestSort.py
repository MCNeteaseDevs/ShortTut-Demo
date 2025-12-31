from demoSortScript.util.sortable import Sortable


class ChestSort(Sortable):
    def __init__(self):
        Sortable.__init__(self)
        self.pos = (0, 0, 0)
        self.dim = 0

    def Update(self, args):
        self.pos = args["pos"]
        self.dim = args["dim"]

    def GetSize(self):
        return self.itemComp.GetContainerSize(self.pos, self.dim)

    def GetContainerItem(self, index):
        return self.itemComp.GetContainerItem(self.pos, index, self.dim, True)

    def SetContainerItem(self, index, item):
        self.itemComp.SpawnItemToContainer(item, index, self.pos, self.dim)
