# -*- coding: utf-8 -*-

import random
import mod.server.extraServerApi as serverApi
import demoPlayerLootScript.playerLootConst as playerLootConst
from mod_log import logger

ServerSystem = serverApi.GetServerSystemCls()


class PlayerLootServerSystem(ServerSystem):
    """
    该mod的服务端类
    """

    def __init__(self, namespace, systemName):
        ServerSystem.__init__(self, namespace, systemName)
        self.ListenForEvent(
            serverApi.GetEngineNamespace(),
            serverApi.GetEngineSystemName(),
            "PlayerDieEvent",
            self,
            self.OnPlayerDieEvent,
        )

    def Destroy(self):
        self.UnListenForEvent(
            serverApi.GetEngineNamespace(),
            serverApi.GetEngineSystemName(),
            "PlayerDieEvent",
            self,
            self.OnPlayerDieEvent,
        )

    def OnPlayerDieEvent(self, args):
        player_id = args.get("id")
        if not player_id:
            return

        comp_factory = serverApi.GetEngineCompFactory()
        pos_comp = comp_factory.CreatePos(player_id)
        rot_comp = comp_factory.CreateRot(player_id)
        dim_comp = comp_factory.CreateDimension(player_id)
        item_comp = comp_factory.CreateItem(player_id)

        pos = pos_comp.GetFootPos()
        rot = rot_comp.GetRot()
        dimension_id = dim_comp.GetEntityDimensionId()

        soul_entity_id = self.CreateEngineEntityByTypeStr("demo:soul", pos, rot, dimension_id)
        if not soul_entity_id:
            logger.warn("%s CreateEngineEntityByTypeStr failed", playerLootConst.ModName)
            return

        soul_item_comp = comp_factory.CreateItem(soul_entity_id)
        minecraft_enum = serverApi.GetMinecraftEnum()
        item_pos_type = minecraft_enum.ItemPosType

        inventory_items = item_comp.GetPlayerAllItems(item_pos_type.INVENTORY)
        carried_items = item_comp.GetPlayerAllItems(item_pos_type.CARRIED)
        offhand_items = item_comp.GetPlayerAllItems(item_pos_type.OFFHAND)
        armor_items = item_comp.GetPlayerAllItems(item_pos_type.ARMOR)

        all_items = []
        for item_dict in (inventory_items or []):
            if item_dict:
                all_items.append(item_dict)
        for item_dict in (carried_items or []):
            if item_dict:
                all_items.append(item_dict)
        for item_dict in (offhand_items or []):
            if item_dict:
                all_items.append(item_dict)
        for item_dict in (armor_items or []):
            if item_dict:
                all_items.append(item_dict)

        random.shuffle(all_items)
        for slot, item_dict in enumerate(all_items[:27]):
            soul_item_comp.SetEntityItem(item_pos_type.INVENTORY, item_dict, slot)

        clear_item = {"itemName": "minecraft:air", "count": 0}
        items_dict_map = {}
        for slot in range(len(inventory_items or [])):
            items_dict_map[(item_pos_type.INVENTORY, slot)] = clear_item
        for slot in range(len(carried_items or [])):
            items_dict_map[(item_pos_type.CARRIED, slot)] = clear_item
        for slot in range(len(offhand_items or [])):
            items_dict_map[(item_pos_type.OFFHAND, slot)] = clear_item

        armor_slot_type = minecraft_enum.ArmorSlotType
        armor_slots = [
            armor_slot_type.HEAD,
            armor_slot_type.BODY,
            armor_slot_type.LEG,
            armor_slot_type.FOOT,
        ]
        for slot in armor_slots:
            items_dict_map[(item_pos_type.ARMOR, slot)] = clear_item

        item_comp.SetPlayerAllItems(items_dict_map)
