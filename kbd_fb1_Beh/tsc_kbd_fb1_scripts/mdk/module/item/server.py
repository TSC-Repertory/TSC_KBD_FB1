# -*- coding:utf-8 -*-


from const import *
from ..system.base import *


class ItemModuleServer(ModuleServerBase):
    """物品模块服务端"""
    __mVersion__ = 2
    __identifier__ = ModuleEnum.identifier

    def __init__(self):
        super(ItemModuleServer, self).__init__()
        self._food_recall = {}

    def OnDestroy(self):
        del self._food_recall
        super(ItemModuleServer, self).OnDestroy()

    def ConfigEvent(self):
        super(ItemModuleServer, self).ConfigEvent()
        self.defaultEvent.update({
            ServerEvent.PlayerEatFoodServerEvent: self.PlayerEatFoodServerEvent
        })

    # -----------------------------------------------------------------------------------

    """食物相关"""

    def RegisterFoodRecall(self, item_name, recall):
        # type: (str, any) -> None
        """注册使用食物回调"""
        if item_name not in self._food_recall:
            self._food_recall[item_name] = set()
        food_recall = self._food_recall[item_name]  # type: set
        food_recall.add(recall)

    def UnRegisterFoodRecall(self, item_name, recall):
        # type: (str, any) -> None
        """反注册使用食物回调"""
        food_recall = self._food_recall.get(item_name)  # type: set
        if not food_recall:
            return
        food_recall.discard(recall)
        if not food_recall:
            self._food_recall.pop(item_name, None)

    # -----------------------------------------------------------------------------------

    def PlayerEatFoodServerEvent(self, args):
        item_dict = args["itemDict"]  # type: dict
        item_name = item_dict["itemName"]

        food_recall = self._food_recall.get(item_name)  # type: set
        if not food_recall:
            return
        for recall in food_recall:
            recall(args)
