# -*- coding:utf-8 -*-


import json

import mod.client.extraClientApi as clientApi

from ...common.item import ItemBase
from ...common.utils.misc import Misc


class ClientItem(ItemBase):
    """客户端物品方法"""
    __mVersion__ = 4

    _basic_storage = {}

    @classmethod
    def GetItemInfo(cls, newItemName, newAuxValue=0):
        # type: (str, int) -> dict
        """
        获得物品基础数据\n
        - itemName: str 本地化的物品名字
        - maxStackSize: int 物品最大堆叠数目
        - maxDurability: int 物品最大耐久值
        - id_Aux: int 主要用于客户端的ui绑定，详见客户端接口
        - tierDict: dict 自定义方块定义的挖掘相关的属性 netease:tier,没有设置时返回None
        - itemCategory: str 创造栏分类
        - itemType: str 物品类型
        - itemTierLevel: int 工具等级
        - fuelDuration: float 燃料时长
        - foodNutrition: int 食物营养值
        - foodSaturation: float 食物饱食度
        - weaponDamage: int 武器攻击力
        - armorDefense: int 防具防御力
        """
        comp_factory = clientApi.GetEngineCompFactory()
        item_comp = comp_factory.CreateItem(clientApi.GetLevelId())
        return item_comp.GetItemBasicInfo(newItemName, newAuxValue)

    @classmethod
    def GetItemName(cls, name, auxValue=0):
        # type: (str, int) -> str
        """获得物品中文名字"""
        comp_factory = clientApi.GetEngineCompFactory()
        item_comp = comp_factory.CreateItem(clientApi.GetLevelId())
        return item_comp.GetItemBasicInfo(name, auxValue).get("itemName")

    @staticmethod
    def GetItemTips(item):
        # type: (dict) -> [str]
        """
        获取物品显示信息\n
        以空行标识返回列表元素
        """
        tips = item.get("customTips", "")
        return tips.split("\n")

    @classmethod
    def GetItemExtraId(cls, item):
        # type: (dict) -> dict
        """获取物品自定义数据"""
        extraId = item.get("extraId", {})
        data = {}
        try:
            data = Misc.UnicodeConvert(json.loads(extraId))
            if not isinstance(data, dict):
                print "[info]", "物品解析非法数据：%s" % data
                data = {}
        except ValueError:
            print "[info]", "物品解析非字典内容：%s" % extraId
        finally:
            return data
