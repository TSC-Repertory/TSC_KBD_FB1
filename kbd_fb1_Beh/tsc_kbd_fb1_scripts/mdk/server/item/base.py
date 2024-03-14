# -*- coding:utf-8 -*-


import copy
import json

import mod.server.extraServerApi as serverApi

from ...common.item import ItemBase
from ...common.system.base import GameBlock


class ItemUserData(object):
    """物品玩家数据"""

    def __init__(self):
        self.storage = {}

    @classmethod
    def Create(cls):
        """创建一个物品玩家数据"""
        return ItemUserData()

    def Export(self):
        """输出一个物品玩家数据"""
        return copy.deepcopy(self.storage)

    # -----------------------------------------------------------------------------------

    def AddKeepInventory(self):
        """添加死亡不掉落"""
        self.storage.update({
            'minecraft:keep_on_death': {
                '__type__': 1,
                '__value__': 1
            }
        })
        return self


class ServerItem(ItemBase):
    """服务端物品管理"""
    __mVersion__ = 3

    @classmethod
    def Create(cls, itemName, **kwargs):
        # type: (str, any) -> dict
        """创建一个原版格式的物品字典"""
        count = kwargs.get("count", 1)
        if not count:
            return {}
        extraId = kwargs.get("extraId", {})
        customTips = kwargs.get("customTips", "")

        item_dict = {
            "newItemName": itemName,
            "newAuxValue": kwargs.get("newAuxValue", 0),
            "count": count,
            "customTips": "",
            "extraId": "",
            "showInHand": kwargs.get("showInHand", True)
        }
        userData = kwargs.get("userData")
        if userData:
            item_dict["userData"] = userData

        if kwargs.get("modify") or extraId:
            cls.SetExtraId(item_dict, extraId)
        cls.SetTips(item_dict, customTips)

        return item_dict

    @classmethod
    def CreateBlockItem(cls, itemName, **kwargs):
        """创建一个原版格式的物品字典"""
        level_id = serverApi.GetLevelId()
        player_id = serverApi.GetPlayerList()[0]
        comp_factory = serverApi.GetEngineCompFactory()
        item_comp = comp_factory.CreateItem(level_id)
        block_comp = comp_factory.CreateBlockInfo(level_id)
        # -----------------------------------------------------------------------------------
        dim = comp_factory.CreateDimension(player_id).GetEntityDimensionId()
        posX, _, posZ = comp_factory.CreatePos(player_id).GetPos()
        posX, posZ = int(posX), int(posZ)
        posY = int(block_comp.GetTopBlockHeight((posX, posZ), dim)) + 1
        pos = (posX, posY, posZ)
        # -----------------------------------------------------------------------------------
        show_in_hand = kwargs.get("showInHand", True)
        block_comp.SetBlockNew(pos, {"name": "minecraft:chest", "aux": 0}, 0, dim)
        item_comp.SpawnItemToContainer({"newItemName": itemName, "count": 1, "showInHand": show_in_hand}, 0, pos, dim)
        item = item_comp.GetContainerItem(pos, 0, dim)
        block_comp.SetBlockNew(pos, {"name": "minecraft:air", "aux": 0}, 0, dim)
        # -----------------------------------------------------------------------------------
        item.update(**kwargs)
        return item

    # -----------------------------------------------------------------------------------

    @classmethod
    def GetVoid(cls):
        # type: () -> dict
        """
        获得空气物品字典\n
        - 用于填充物品或方块空格
        """
        return cls.Create(GameBlock.air)

    # -----------------------------------------------------------------------------------

    @classmethod
    def SpawnAtPos(cls, item_dict, atPos, atDim):
        # type: (dict, tuple, int) -> bool
        """生成一个物品"""
        item_comp = serverApi.GetEngineCompFactory().CreateItem(serverApi.GetLevelId())
        return item_comp.SpawnItemToLevel(item_dict, atDim, atPos)

    @classmethod
    def SpawnAtPosByName(cls, itemName, pos, dim, **kwargs):
        """生成一个物品"""
        kwargs.get("userData")
        kwargs.get("showInHand")
        item = cls.Create(itemName, **kwargs)
        return cls.SpawnAtPos(item, pos, dim)

    # -----------------------------------------------------------------------------------

    @classmethod
    def GetCustomName(cls, item_dict):
        # type: (dict) -> str
        """
        获得物品名称\n
        - 需要包含userData
        - 优先自定义名称
        """
        item_comp = serverApi.GetEngineCompFactory().CreateItem(serverApi.GetLevelId())
        item_name = item_comp.GetCustomName(item_dict)
        return item_name

    # -----------------------------------------------------------------------------------

    @staticmethod
    def SetTips(item_dict, tip):
        # type: (dict, str) -> None
        """设置物品显示"""
        item_dict["customTips"] = tip

    @classmethod
    def AddTips(cls, item_dict, tip):
        # type: (dict, str) -> None
        """添加物品显示\n
        问题：原本格式需要空行操作时
        """
        tips = cls.GetTips(item_dict).split("\n")
        tips.append(tip)
        item_dict["customTips"] = "\n".join(tips)

    @classmethod
    def ResetTips(cls, item_dict):
        # type: (dict) -> None
        """
        重置物品显示\n
        只显示物品的名字
        """
        item_name = cls.GetLocalName(item_dict["newItemName"])
        cls.SetTips(item_dict, item_name)

    # -----------------------------------------------------------------------------------

    @classmethod
    def GetMaxStack(cls, itemName):
        # type: (str) -> int
        """获得物品最大堆叠数"""
        item_comp = serverApi.GetEngineCompFactory().CreateItem(serverApi.GetLevelId())
        item_info = item_comp.GetItemBasicInfo(itemName)
        return item_info.get("maxStackSize")

    # -----------------------------------------------------------------------------------

    @classmethod
    def AddExtraId(cls, item_dict, pack):
        # type: (dict, dict) -> None
        """
        更新物品自定义数据\n
        以字典更新方式更新
        """
        data = cls.GetExtraId(item_dict)
        data.update(copy.deepcopy(pack))
        item_dict["extraId"] = json.dumps(data)

    @staticmethod
    def SetExtraId(item_dict, pack):
        # type: (dict, dict) -> None
        """设置物品自定义数据"""
        item_dict["extraId"] = json.dumps(copy.deepcopy(pack))

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
        item_comp = serverApi.GetEngineCompFactory().CreateItem(serverApi.GetLevelId())
        return item_comp.GetItemBasicInfo(newItemName, newAuxValue)

    @classmethod
    def LookupItemByName(cls, itemName):
        # type: (str) -> bool
        """判定指定identifier的物品是否存在"""
        game_comp = serverApi.GetEngineCompFactory().CreateGame(serverApi.GetLevelId())
        return game_comp.LookupItemByName(itemName)
