# -*- coding:utf-8 -*-


import re

from mod.common.minecraftEnum import ItemPosType

from ...common.system.base import *


class ServerInventoryMgr(object):
    """服务端玩家背包管理"""
    __mVersion__ = 8

    def __init__(self, playerId):
        self.id = playerId
        self.item_comp = serverApi.GetEngineCompFactory().CreateItem(self.id)

    def AddItem(self, item):
        # type: (dict) -> None
        """添加物品"""
        system = MDKConfig.GetModuleServer()
        system.DelayTickFunc(1, lambda: self.item_comp.SpawnItemToPlayerInv(item, self.id))

    def HasItem(self, item_name):
        # type: (str) -> bool
        """判断玩家背包是否有目标物品"""
        for item in self.GetAllItems().itervalues():
            if item and item["newItemName"] == item_name:
                return True
        return False

    def DelItem(self, slot):
        # type: (int) -> None
        """删除玩家背包物品"""
        system = MDKConfig.GetModuleServer()
        system.DelayTickFunc(1, lambda: self.item_comp.SetInvItemNum(slot, 0))

    # -----------------------------------------------------------------------------------

    def GetSelectedSlot(self):
        # type: () -> int
        """获得手持槽位"""
        return self.item_comp.GetSelectSlotId()

    def GetSelectedItem(self):
        # type: () -> dict
        """获得手持物品"""
        item = self.GetItemBySlot(self.item_comp.GetSelectSlotId())
        if not item:
            return {}
        return item

    def DelSelectedItem(self):
        """删除手持物品"""
        system = MDKConfig.GetModuleServer()
        system.DelayTickFunc(1, lambda: self.SetSlotItemNum(self.GetSelectedSlot(), 0))

    def DelSelectedItemNum(self, num):
        """删除手持物品数量"""
        slot = self.GetSelectedSlot()
        count = self.GetSlotItemNum(slot)
        count = max(0, count - num)
        self.SetSlotItemNum(slot, count)

    # -----------------------------------------------------------------------------------

    def GetDataCache(self):
        # type: () -> dict
        """
        获得背包缓存\n
        - item = {newItemName: count}
        """
        cache = dict()
        for item in self.GetAllItems().itervalues():
            if not item:
                continue
            item_name = item["newItemName"]  # type: str
            cache[item_name] = item["count"] + cache.get(item_name, 0)
        return cache

    # -----------------------------------------------------------------------------------

    def GetAllItems(self):
        # type: () -> dict
        """
        获得玩家所有物品\n
        - key: int 槽位号
        - value: dict|None 物品字典或None
        """
        inventory = self.item_comp.GetPlayerAllItems(ItemPosType.INVENTORY, getUserData=True)
        return {key: value for key, value in zip(xrange(len(inventory)), inventory)}

    def GetAllItemsFormat(self):
        # type: () -> dict
        """按Java版格式获得玩家所有物品"""
        inventory = self.item_comp.GetPlayerAllItems(ItemPosType.INVENTORY, getUserData=True)
        return {"slot%s" % key: value for key, value in zip(xrange(len(inventory)), inventory)}

    def SetAllItems(self, storage):
        # type: (dict) -> None
        """设置玩家背包栏"""
        item_map = {}
        for slot, item in storage.iteritems():
            slot = int(slot)
            item_map[(ItemPosType.INVENTORY, slot)] = item
            self.SetItemBySlot(item, slot)

    # -----------------------------------------------------------------------------------

    def GetItemList(self, item_name):
        # type: (str) -> list
        """获取目标物品所在的槽位列表"""
        res = []
        for slot, item in self.GetAllItems().iteritems():
            if item and item["newItemName"] == item_name:
                res.append(slot)
        return res

    def GetFormatItemList(self, formatStr):
        # type: (str) -> list
        """获取目标格式物品所在的槽位列表"""
        res = []
        for slot, item in self.GetAllItems().iteritems():
            if item and re.findall(formatStr, item["newItemName"]):
                res.append(slot)
        return res

    def GetEmptySlotList(self):
        # type: () -> list
        """获得空槽位列表"""
        res = []
        for slot, item in self.GetAllItems().iteritems():
            if not item:
                res.append(slot)
        return res

    # -----------------------------------------------------------------------------------

    def GetItemBySlot(self, slot):
        # type: (int) -> dict
        """根据槽位获得物品"""
        item = self.item_comp.GetPlayerItem(ItemPosType.INVENTORY, slot, True)
        if not item:
            return {}
        return item

    def GetItemBySlotKey(self, slot):
        # type: (str) -> dict
        """
        根据槽位键获得物品\n
        - slot0 slot1
        """
        return self.GetItemBySlot(int(slot.replace("slot", "")))

    def SetItemBySlot(self, item, slot):
        # type: (dict, int) -> None
        """根据槽位索引设置物品"""
        if item:
            self.item_comp.SpawnItemToPlayerInv(item, self.id, slot)
        else:
            self.item_comp.SetInvItemNum(slot, ItemPosType.INVENTORY)

    def SetItemBySlotKey(self, slot, item):
        # type: (str, dict) -> None
        """根据槽位键设置物品"""
        return self.SetItemBySlot(item, int(slot.replace("slot", "")))

    # -----------------------------------------------------------------------------------

    def DelItemTypeNum(self, item_name, num=1, hard=False):
        # type: (str, int, bool) -> bool
        """
        删除一定数量的目标物品\n
        成功清除时不一定按顺序清除物品\n
        - 不满足数量时不会清除 返回False
        - 满足数量条件则会清除 返回True
        """
        storage = self.GetAllItems()
        for slot, item in storage.items():
            if item and item["newItemName"] == item_name:
                count = item["count"]
                # 完成清除数量
                if count > num:
                    item["count"] = count - num
                    num = 0
                    break
                else:
                    # 清除物品
                    storage[slot] = {}
                    num -= count
        if num > 0 and not hard:
            return False

        self.SetAllItems(storage)
        return True

    def DelBatchItemTypeNum(self, items, hard=False):
        # type: (dict, bool) -> bool
        """
        删除一定数量的批量物品\n
        - items: dict -> item_name: del_num
        """
        storage = self.GetAllItems()
        for slot, item in storage.items():
            if not item:
                continue
            item_name = item["newItemName"]
            if item_name not in items:
                continue
            del_num = items[item_name]
            if del_num <= 0:
                continue
            count = item["count"]
            # 完成清除数量
            if count > del_num:
                item["count"] = count - del_num
                items[item_name] = 0
                if not all(items.items()):
                    break
            else:
                # 清除物品
                storage[slot] = {}
                items[item_name] -= count
        if not all(items.items()) and not hard:
            return False

        self.SetAllItems(storage)
        return True

    def GetItemTypeNum(self, item_name):
        # type: (str) -> int
        """获得目标物品的数量"""
        count = 0
        for item in self.GetAllItems().itervalues():
            if item and item["newItemName"] == item_name:
                count += item["count"]
        return count

    # -----------------------------------------------------------------------------------

    def GetSlotItemNum(self, slot):
        # type: (int) -> int
        """获取槽位物品的数量"""
        item = self.item_comp.GetPlayerItem(ItemPosType.INVENTORY, slot, True)
        if not item:
            return 0
        return item["count"]

    def SetSlotItemNum(self, slot, num):
        # type: (int, int) -> bool
        """设置槽位物品数量"""
        return self.item_comp.SetInvItemNum(slot, num)

    def DelSlotItemNum(self, slot, num=1):
        # type: (int, int) -> bool
        """删除槽位物品数量"""
        count = self.GetSlotItemNum(slot)
        if count <= num:
            self.DelItem(slot)
            return count == num
        else:
            self.SetSlotItemNum(slot, count - num)
            return True

    # -----------------------------------------------------------------------------------

    @staticmethod
    def CanMergeItems(itemA, itemB):
        # type: (dict, dict) -> tuple
        """判断两个物品是否可以合并"""
        if not itemA or not itemB:
            return False, {}

        nameA, nameB = itemA["newItemName"], itemB["newItemName"]
        if nameA != nameB:
            return False, {}

        auxA, auxB = itemA["newAuxValue"], itemB["newAuxValue"]
        if auxA != auxB:
            return False, {}

        if itemA.get("extraId") != itemB.get("extraId"):
            return False, {}
        if itemA.get("customTips") != itemB.get("customTips"):
            return False, {}

        from base import ServerItem
        maxStack = ServerItem.GetMaxStack(nameA)

        countA, countB = itemA.get("count"), itemB.get("count")

        if countA >= 64 or countB >= 64:
            return False, {}

        countB += countA
        if countB >= maxStack:
            countA = countB - maxStack
            countB = maxStack
        else:
            countA = 0

        return True, {
            "countA": countA,
            "countB": countB
        }

    def SetMergeItems(self, slot_a, slot_b):
        # type: (int, int) -> bool
        """
        合并玩家背包物品\n
        order: slot_a merge into slot_b
        """
        itemA = self.GetItemBySlot(slot_a)
        itemB = self.GetItemBySlot(slot_b)

        can_merge, res = self.CanMergeItems(itemA, itemB)
        if not can_merge:
            return False

        self.item_comp.SetInvItemNum(slot_a, res["countA"])
        self.item_comp.SetInvItemNum(slot_b, res["countB"])
        return True

    def SetMergeBySlotKey(self, slot_a, slot_b):
        # type: (str, str) -> bool
        """
        根据槽位键合并玩家背包物品\n
        order: slot_a merge into slot_b
        """
        return self.SetMergeItems(int(slot_a.replace("slot", "")), int(slot_b.replace("slot", "")))

    def SetExchangeItems(self, slot_a, slot_b):
        # type: (int, int) -> bool
        """交换玩家背包物品"""
        return self.item_comp.SetInvItemExchange(slot_a, slot_b)

    def SetExchangeBySlotKey(self, slot_a, slot_b):
        # type: (str, str) -> bool
        """根据槽位键交换玩家背包物品"""
        return self.SetExchangeItems(int(slot_a.replace("slot", "")), int(slot_b.replace("slot", "")))
