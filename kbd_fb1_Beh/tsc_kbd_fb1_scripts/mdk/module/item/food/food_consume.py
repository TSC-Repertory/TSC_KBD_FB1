# -*- coding:utf-8 -*-


import copy

from ..common.base import *
from ..const import ModuleEnum, ModuleEvent


class ItemFoodConsumeModuleServer(ItemModuleServerBase):
    """食物物品消化模块服务端"""
    __mVersion__ = 3
    __identifier__ = ModuleEnum.food_consume
    _ModuleRequestRegisterEvent = ModuleEvent.ModuleRequestItemFoodConsumeRegisterEvent
    _data_config = {
        "storage_key": "ItemFoodConsumeStorage",  # 数据键
        "syn_data_key": ""  # 同步数据键 - 客户端缓存
    }

    def __init__(self):
        super(ItemFoodConsumeModuleServer, self).__init__()
        self.active_player = set()
        self.food_storage = {}
        self.use_time = 10
        self.ban_item = []
        self.LoadData()

    def OnDestroy(self):
        self.ModuleSystem.UnRegisterUpdateSecond(self.OnUpdateSecond)
        self.SaveData()
        super(ItemFoodConsumeModuleServer, self).OnDestroy()

    def ConfigEvent(self):
        super(ItemFoodConsumeModuleServer, self).ConfigEvent()
        self.defaultEvent[ServerEvent.ClientLoadAddonsFinishServerEvent] = self.ClientLoadAddonsFinishServerEvent
        self.defaultEvent[ServerEvent.PlayerIntendLeaveServerEvent] = self.PlayerIntendLeaveServerEvent
        self.defaultEvent[ServerEvent.PlayerEatFoodServerEvent] = self.PlayerEatFoodServerEvent

    def ConfigRegisterData(self):
        self.RegisterData("food_storage", {})
        self.RegisterData("use_time", 10)
        self.RegisterData("ban_item", [])

    # -----------------------------------------------------------------------------------

    def OnLoadModConfig(self, data):
        return True

    # -----------------------------------------------------------------------------------

    def SetGlobalUseTime(self, use_time):
        self.use_time = use_time
        self.SaveData()

    def SetGlobalBanItem(self, items):
        # type: (list) -> None
        """
        设置全局无效物品\n
        - 食用无效物品不会进入逻辑
        """
        self.ban_item = list(set(self.ban_item) | set(items))
        self.SynData()

    # -----------------------------------------------------------------------------------

    def OnUpdateSecond(self):
        """秒更新"""
        for playerId in list(self.active_player):
            if playerId not in self.food_storage:
                return
            food_storage = self.food_storage[playerId]  # type: dict
            use_time = food_storage["use_time"]  # type: list
            pop_array = []
            for index, food_time in enumerate(use_time):
                food_time -= 1
                if food_time <= 0:
                    pop_array.append(index)
                else:
                    use_time[index] = food_time
            if pop_array:
                self.flag_syn_data = True
                food_item = food_storage["food_item"]  # type: list
                for index in pop_array[::-1]:
                    use_time.pop(index)
                    food_item.pop(index)
                if not food_item:
                    self.food_storage.pop(playerId, None)
        if self.flag_syn_data:
            self.SaveData()

    def OnPlayerEatFood(self, player_id, item_name, hunger, nutrition):
        """玩家使用食物"""
        if player_id not in self.food_storage:
            self.food_storage[player_id] = {"food_item": [], "use_time": []}
        food_storage = self.food_storage[player_id]  # type: dict
        food_item = food_storage["food_item"]  # type: list
        data_pack = {
            "playerId": player_id,
            "item_name": item_name,
            "items": copy.copy(food_item),
            "cancel": False
        }
        self.BroadcastEvent(ModuleEvent.BeforeFoodItemGainNewFoodEvent, data_pack)
        if data_pack.get("cancel"):
            return
        food_item.append(item_name)
        food_storage["use_time"].append(self.use_time)
        self.BroadcastEvent(ModuleEvent.OnFoodItemGainNewFoodEvent, {
            "playerId": player_id,
            "food_item": food_item,
            "hunger": hunger,
            "nutrition": nutrition
        })
        self.flag_syn_data = True

    # -----------------------------------------------------------------------------------

    def ClientLoadAddonsFinishServerEvent(self, args):
        playerId = args["playerId"]
        self.active_player.add(playerId)

    def PlayerIntendLeaveServerEvent(self, args):
        playerId = args["playerId"]
        self.active_player.discard(playerId)

    def PlayerEatFoodServerEvent(self, args):
        hunger = args["hunger"]
        if not hunger:
            return
        player_id = args["playerId"]
        item_dict = args["itemDict"]  # type: dict
        item_name = item_dict["itemName"]
        if item_name in self.ban_item:
            return
        nutrition = args["nutrition"]
        self.OnPlayerEatFood(player_id, item_name, hunger, nutrition)
