# -*- coding:utf-8 -*-


from ..item.predicate import ItemPredicate
from mod.common.minecraftEnum import ItemPosType
from ..parts.base import ConditionBase


# 工具匹配检测条件
class MatchToolCondition(ConditionBase):
    """工具匹配检测条件"""
    __mVersion__ = 1

    def Parse(self):
        predicate = self.data["predicate"]  # 物品通用解析
        item_comp = self.comp_factory.CreateItem(self.predicate_id)
        if self.comp_factory.CreateEngineType(self.predicate_id).GetEngineTypeStr() == "minecraft:player":
            item_dict = item_comp.GetPlayerItem(ItemPosType.CARRIED, 0, True)
        else:
            item_dict = item_comp.GetEntityItem(ItemPosType.CARRIED, 0, True)
        if not item_dict:
            return False
        return ItemPredicate(item_dict, predicate, self.context).GetResult()
