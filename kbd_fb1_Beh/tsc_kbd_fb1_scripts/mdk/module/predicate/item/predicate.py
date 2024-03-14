# -*- coding:utf-8 -*-


import mod.server.extraServerApi as serverApi
from ..parts.base import PredicateBase


class ItemPredicate(PredicateBase):
    """物品断言"""
    __mVersion__ = 2

    def __init__(self, item, data, context=None):
        super(ItemPredicate, self).__init__(data, context)
        self.item = item  # type: dict

    """
    newItemName	str	必须设置，物品的identifier，即"命名空间:物品名"
    newAuxValue	int	必须设置，物品附加值
    count	int	必须设置，物品数量。设置为0时为空物品
    showInHand	bool	可选，是否显示在手上，默认为True
    enchantData	list(tuple(EnchantType, int))	可选，附魔数据，tuple中 EnchantType 为附魔类型，int为附魔等级
    modEnchantData	list(tuple(str, int))	可选，自定义附魔数据，tuple中str为自定义附魔id，int为自定义附魔等级
    customTips	str	可选，物品的自定义tips，修改该内容后会覆盖实例的组件netease:customtips的内容
    extraId	str	可选，物品自定义标识符。可以用于保存数据， 区分物品
    userData	dict	可选，物品userData，用于灾厄旗帜、旗帜等物品，请勿随意设置该值
    durability	int	可选，物品耐久度，不存在耐久概念的物品默认值为零
    """

    def Parse(self):

        # 物品数量检测
        key = "count"
        if key in self.data:
            value = self.data[key]
            item_count = self.item[key]
            if not self.TestValue(value, item_count):
                return False
        # 物品名称检测
        key = "items"
        if key in self.data:
            value = self.data[key]
            item_name = self.item["newItemName"]
            if item_name not in value:
                return False
        # 物品耐久检测
        key = "duration"
        if key in self.data:
            value = self.data[key]
            item_duration = self.item["durability"]
            if not self.TestValue(value, item_duration):
                return False
        # 物品附魔检测
        # key = "enchantments"
        # if key in self.data:
        #     value = self.data[key]
        #     # todo: 附魔内容补充
        #     item_enchantments = self.item["enchantData"]  # type: list
        #     if not item_enchantments:
        #         return False
        #     print "[debug]", "item_enchantments -> ", item_enchantments
        return True
