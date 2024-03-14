# -*- coding:utf-8 -*-


import mod.server.extraServerApi as serverApi
from mod.common.minecraftEnum import ItemPosType

from skill_entity import SkillEntity


class LivingEntity(SkillEntity):
    """生物实体基类"""
    __mVersion__ = 7

    def SetCanFly(self, active):
        # type: (bool) -> None
        """设置可以飞行状态"""
        self.comp_factory.CreateFly(self.id).ChangePlayerFlyState(active)

    def SetTameOwner(self, ownerId):
        # type: (str) -> bool
        """设置实体的属主"""
        return self.comp_factory.CreateActorOwner(self.id).SetEntityOwner(ownerId)

    def SetTame(self, ownerId):
        # type: (str) -> bool
        """设置实体驯服"""
        return self.comp_factory.CreateTame(self.id).SetEntityTamed(ownerId, self.id)

    def GetTameOwner(self):
        """获得实体驯服主人"""
        return self.comp_factory.CreateTame(self.id).GetOwnerId()

    def SetRidePos(self, pos):
        # type: (tuple) -> bool
        """设置生物骑乘位置"""
        return self.comp_factory.CreateRide(serverApi.GetLevelId()).SetRidePos(self.id, pos)

    # -----------------------------------------------------------------------------------

    def GetSelectedItem(self):
        # type: () -> dict
        """获得手持物字典"""
        item_comp = self.comp_factory.CreateItem(self.id)
        item_dict = item_comp.GetEntityItem(ItemPosType.CARRIED, getUserData=True)
        if not item_dict:
            item_dict = {}
        return item_dict

    def SetSelectedItem(self, itemDict):
        # type: (dict) -> bool
        """设置生物主手物品"""
        item_comp = self.comp_factory.CreateItem(self.id)
        return item_comp.SetEntityItem(ItemPosType.CARRIED, itemDict)

    def GetSelectedItemName(self):
        # type: () -> str
        """获得主手物品Id"""
        return self.GetSelectedItem().get("newItemName", "")

    def GetOffhandItem(self):
        # type: () -> dict
        """获得副手物品字典"""
        item_comp = self.comp_factory.CreateItem(self.id)
        itemDict = item_comp.GetEntityItem(ItemPosType.OFFHAND, getUserData=True)
        if not itemDict:
            itemDict = {}
        return itemDict

    def GetOffhandItemName(self):
        # type: () -> str
        """获得副手物品Id"""
        return self.GetOffhandItem().get("newItemName", "")

    def SetOffhandItem(self, itemDict):
        # type: (dict) -> bool
        """设置生物副手物品"""
        item_comp = self.comp_factory.CreateItem(self.id)
        return item_comp.SetEntityItem(ItemPosType.OFFHAND, itemDict)

    def GetArmorItem(self, slotPos):
        # type: (int) -> dict
        """获取实体的装备"""
        item_comp = self.comp_factory.CreateItem(self.id)
        return item_comp.GetEntityItem(ItemPosType.ARMOR, slotPos, True)

    def GetArmorItemName(self, slot_pos):
        # type: (int) -> str
        """获得实体装备名称"""
        item = self.GetArmorItem(slot_pos)
        if not item:
            return ""
        return item["newItemName"]

    def GetHelmetItem(self):
        # type: () -> dict
        """获得实体头盔物品"""
        return self.GetArmorItem(0)

    def GetChestplateItem(self):
        # type: () -> dict
        """获得实体胸甲物品"""
        return self.GetArmorItem(1)

    def GetLeggingsItem(self):
        # type: () -> dict
        """获得实体护腿物品"""
        return self.GetArmorItem(2)

    def GetBootsItem(self):
        # type: () -> dict
        """获得实体护腿物品"""
        return self.GetArmorItem(3)

    def SetArmorItem(self, slotPos, itemDict):
        # type: (int, dict) -> bool
        """设置实体的装备"""
        item_comp = self.comp_factory.CreateItem(self.id)
        return item_comp.SetEntityItem(ItemPosType.ARMOR, itemDict, slotPos)
