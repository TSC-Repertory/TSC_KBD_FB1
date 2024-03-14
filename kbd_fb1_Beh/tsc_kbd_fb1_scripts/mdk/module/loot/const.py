# -*- coding:utf-8 -*-


import copy

import mod.server.extraServerApi as serverApi

from ..predicate import *


class ModuleEnum(object):
    """模块枚举"""
    identifier = "loot"


class ModuleEvent(object):
    """模块事件"""
    ModuleRequestLootRegisterEvent = "ModuleRequestLootRegisterEvent"  # 请求注册配置事件


class ModuleLootEnum(object):
    """战利品枚举"""

    LootConfig = {}
    VanillaLootConfig = {}

    @classmethod
    def GetConfig(cls, name):
        return cls.LootConfig.get(name, None)


class ModuleParser(EventParserBase):
    """模块解释器"""
    __mVersion__ = 1
    _parser = None

    def __new__(cls, *args, **kwargs):
        if not cls._parser:
            ins = super(ModuleParser, cls).__new__(cls, *args, **kwargs)
            cls._parser = ins
        return cls._parser

    def __init__(self, context):
        super(ModuleParser, self).__init__(context)
        self.item_comp = self.comp_factory.CreateItem(serverApi.GetLevelId())

    @classmethod
    def GetSelf(cls):
        ins = cls._parser
        if not ins:
            ins = ModuleParser({"host": None, "other": None})
        return ins

    def Parse(self, items):
        # type: (list) -> list
        """
        解析添加物品\n
        - items: list<dict>
        """
        dataPack = []
        if not items:
            return []
        items = copy.deepcopy(items)
        for itemConfig in items:
            assert isinstance(itemConfig, dict)
            itemList = [itemConfig]
            if itemConfig.get("type"):
                if not self._conditionParser.Parse(itemConfig):
                    continue
                # todo: 暂时不支持无限解析TypeParser
                itemList = self._typeParser.Parse(itemConfig)
            for item in itemList:
                item["engine_type"] = "minecraft:item"
                if not item.get("count"):
                    item["count"] = 1  # 默认数量
                if not self._conditionParser.Parse(item):
                    continue
                self._funcParser.Parse(item)
                if not item.get("count") >= 1:
                    continue
                # 数据出口格式修正
                itemDict = {
                    "newItemName": item.get("name"),
                    "count": max(1, min(64, item.get("count"))),
                    "showInHand": item.get("show_in_hand", True),
                    "customTips": item.get("lore", "")
                    # 附魔
                    # 附加值
                    # 额外数据
                }
                # 内容修正
                if "customName" in item:
                    self.item_comp.SetCustomName(itemDict, item["customName"])
                dataPack.append(itemDict)
        return dataPack
