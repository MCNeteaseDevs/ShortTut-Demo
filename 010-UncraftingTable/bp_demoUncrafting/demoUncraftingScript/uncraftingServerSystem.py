# -*- coding: utf-8 -*-

import mod.server.extraServerApi as serverApi
import demoUncraftingScript.uncraftingConst as uncraftingConst
from mod_log import logger

ServerSystem = serverApi.GetServerSystemCls()


def calculate_materials(recipe_data):
    """
    兼容有序(pattern)和无序(ingredients)配方的统计函数
    :param recipe_data: 配方字典数据
    :return: 字典 {item_id: 总数量}
    """
    materials_needed = {}

    # --- 情况 1: 处理无序合成 (Shapeless, 也就是你新提供的格式) ---
    if 'ingredients' in recipe_data:
        for entry in recipe_data['ingredients']:
            item_id = entry.get('item')
            data = entry.get('data', 0)
            # 获取数量，如果没有 'count' 字段，默认视为 1
            count = entry.get('count', 1)

            key = (item_id, data)

            if item_id:
                if key not in materials_needed:
                    materials_needed[key] = 0
                materials_needed[key] += count

    # --- 情况 2: 处理有序合成 (Shaped, 之前的 pattern 格式) ---
    elif 'pattern' in recipe_data and 'key' in recipe_data:
        pattern = recipe_data.get('pattern', [])
        ingredient_key = recipe_data.get('key', {})

        for row in pattern:
            for char in row:
                if char == ' ':
                    continue

                # 在 key 中查找定义
                if char in ingredient_key:
                    item_info = ingredient_key[char]
                    item_id = item_info.get('item')
                    data = item_info.get('data', 0)

                    if item_id is list:
                        item_id = item_id[0]
                    key = (item_id, data)

                    if item_id:
                        if key not in materials_needed:
                            materials_needed[key] = 0
                        # 有序配方通常每个字符代表 1 个物品
                        materials_needed[key] += 1

    return materials_needed


class UncraftingServerSystem(ServerSystem):
    """
    该mod的服务端类
    """

    def __init__(self, namespace, systemName):
        ServerSystem.__init__(self, namespace, systemName)
        self.recipeComp = serverApi.GetEngineCompFactory().CreateRecipe(serverApi.GetLevelId())
        self.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), "ServerBlockUseEvent", self, self.OnBlockUse)

    def OnBlockUse(self, args):
        if args["blockName"] != "demo:uncrafting_table":
            return
        args["cancel"] = True
        itemDict = args["itemDict"]
        if not itemDict:
            return
        playerId = args["playerId"]
        results = self.recipeComp.GetRecipesByResult(itemDict["newItemName"], "crafting_table")
        if not results:
            return
        result = results[0]
        print result
        if result["result"][0].get("count", 1) > itemDict["count"]:
            return
        materials = calculate_materials(result)
        itemComp = serverApi.GetEngineCompFactory().CreateItem(playerId)
        for item_key, count in materials.items():
            item_id, data = item_key
            item = {
                "newItemName": item_id,
                "newAuxValue": data,
                "count": count
            }
            itemComp.SetInvItemNum(itemComp.GetSelectSlotId(), itemDict["count"] - 1)
            itemComp.SpawnItemToPlayerInv(item, playerId)
