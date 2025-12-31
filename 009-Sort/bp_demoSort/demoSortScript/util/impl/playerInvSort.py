from mod.common.minecraftEnum import ItemPosType

from demoSortScript.util.sortable import Sortable
import mod.server.extraServerApi as serverApi


class PlayerInvSort(Sortable):
    def __init__(self):
        Sortable.__init__(self)
        self.playerId = ""

    def Update(self, args):
        self.playerId = args["player"]
        self.itemComp = serverApi.GetEngineCompFactory().CreateItem(self.playerId)

    def GetStart(self):
        return 9

    def GetSize(self):
        return 36

    def GetContainerItem(self, index):
        return self.itemComp.GetPlayerItem(ItemPosType.INVENTORY, index, True)

    def SetContainerItem(self, index, item):
        self.itemComp.SpawnItemToPlayerInv(item, self.playerId, index)
