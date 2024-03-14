# -*- coding:utf-8 -*-


import json
import re

from utils.misc import Misc


class ItemBase(object):
    """物品基类"""
    __mVersion__ = 2

    @classmethod
    def GetTips(cls, item):
        # type: (dict) -> str
        """获取物品显示信息"""
        return item.get("customTips", "")

    @classmethod
    def HasTips(cls, itemDict, match):
        # type: (dict, str) -> bool
        """判断物品是否有该显示元素"""
        for tip in cls.GetTips(itemDict).split("\n"):
            if re.findall(match, tip):
                return True
        return False

    # -----------------------------------------------------------------------------------

    @classmethod
    def GetExtraId(cls, itemDict):
        # type: (dict) -> dict
        """获取物品自定义数据"""
        extraId = itemDict.get("extraId", {})
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

    # -----------------------------------------------------------------------------------

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

    @classmethod
    def GetItemType(cls, newItemName, newAuxValue=0):
        # type: (str, int) -> str
        """获得物品类型"""
        info = cls.GetItemInfo(newItemName, newAuxValue)
        return info.get("itemType")

    @classmethod
    def GetLocalName(cls, newItemName, newAuxValue=0):
        # type: (str, int) -> str
        """获得本地化的物品名字"""
        info = cls.GetItemInfo(newItemName, newAuxValue)
        return info.get("itemName")

    @classmethod
    def GetMaxStackSize(cls, newItemName, newAuxValue=0):
        # type: (str, int) -> int
        """获得物品最大堆叠数目"""
        info = cls.GetItemInfo(newItemName, newAuxValue)
        return info.get("maxStackSize")

    @classmethod
    def GetMaxDuration(cls, newItemName, newAuxValue=0):
        # type: (str, int) -> int
        """获得物品最大耐久值"""
        info = cls.GetItemInfo(newItemName, newAuxValue)
        return info.get("maxDurability")

    @classmethod
    def GetItemTierLevel(cls, newItemName, newAuxValue=0):
        # type: (str, int) -> float
        """获得工具等级"""
        info = cls.GetItemInfo(newItemName, newAuxValue)
        return info.get("itemTierLevel")

    @classmethod
    def GetFuelDuration(cls, newItemName, newAuxValue=0):
        # type: (str, int) -> float
        """获得燃料时长"""
        info = cls.GetItemInfo(newItemName, newAuxValue)
        return info.get("fuelDuration")

    @classmethod
    def GetArmorDefense(cls, newItemName, newAuxValue=0):
        # type: (str, int) -> int
        """获得防具防御力"""
        info = cls.GetItemInfo(newItemName, newAuxValue)
        return info.get("armorDefense")

    @classmethod
    def GetWeaponDamage(cls, newItemName, newAuxValue=0):
        # type: (str, int) -> int
        """获得武器攻击力"""
        info = cls.GetItemInfo(newItemName, newAuxValue)
        return info.get("weaponDamage")

    @classmethod
    def GetFoodNutrition(cls, newItemName, newAuxValue=0):
        # type: (str, int) -> int
        """获得食物营养值"""
        info = cls.GetItemInfo(newItemName, newAuxValue)
        return info.get("foodNutrition")

    @classmethod
    def GetFoodSaturation(cls, newItemName, newAuxValue=0):
        # type: (str, int) -> int
        """获得食物饱食度"""
        info = cls.GetItemInfo(newItemName, newAuxValue)
        return info.get("foodSaturation")
