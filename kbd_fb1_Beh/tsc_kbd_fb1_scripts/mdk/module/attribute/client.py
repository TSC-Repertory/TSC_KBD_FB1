# -*- coding:utf-8 -*-


from const import *
from ..system.base import *
from ...client.entity import *


class AttrModuleClient(ModuleClientBase):
    """属性模块客户端"""
    __identifier__ = ModuleEnum.identifier
    __mVersion__ = 6

    def __init__(self):
        super(AttrModuleClient, self).__init__()
        self._register_key = set()
        self._entity_storage = {self.local_id: {}}
        self._entity_update_recall = {}
        self._entity_cache = {}

    def OnDestroy(self):
        del self._entity_update_recall
        super(AttrModuleClient, self).OnDestroy()

    def ConfigEvent(self):
        super(AttrModuleClient, self).ConfigEvent()
        self.defaultEvent.update({
            ClientEvent.AddEntityClientEvent: self.AddEntityClientEvent,
            ClientEvent.RemoveEntityClientEvent: self.RemoveEntityClientEvent,
        })
        self.serverEvent.update({
            ModuleEvent.ModuleRequestSynEntityAttrEvent: self.ModuleRequestSynEntityAttrEvent
        })

    # -----------------------------------------------------------------------------------

    def RegisterEntityUpdateRecall(self, entity_id, recall):
        # type: (str, any) -> bool
        """注册实体数据更新回调"""
        if entity_id not in self._entity_update_recall:
            self._entity_update_recall[entity_id] = set()
        recall_set = self._entity_update_recall[entity_id]  # type: set
        recall_set.add(recall)
        return True

    def UnRegisterEntityUpdateRecall(self, entity_id, recall):
        # type: (str, any) -> None
        """反注册实体数据更新回调"""
        if entity_id not in self._entity_update_recall:
            return
        recall_set = self._entity_update_recall[entity_id]  # type: set
        recall_set.discard(recall)
        if not recall_set:
            self._entity_update_recall.pop(entity_id)

    # -----------------------------------------------------------------------------------

    def GetEntityCache(self, entity_id):
        # type: (str) -> dict
        """获得实体属性缓存 - 只读"""
        return self._entity_storage.get(entity_id, {})

    def GetEntityAttrGroup(self, entity_id, group_key):
        # type: (str, str) -> dict
        """获得实体属性组数据"""
        config = self._entity_storage.get(entity_id, {})
        return config.get(group_key, {})

    def GetEntityAttrValue(self, entity_id, group_key, attr_key):
        # type: (str, str, str) -> any
        """获得实体属性组属性值"""
        return self.GetEntityAttrGroup(entity_id, group_key).get(attr_key)

    def GetAttrGroup(self, group_key):
        # type: (str) -> dict
        """获得玩家属性组数据"""
        return self.GetEntityAttrGroup(self.local_id, group_key)

    def GetAttrValue(self, group_key, attr_key):
        # type: (str, str) -> any
        """获得玩家属性组属性值"""
        return self.GetEntityAttrValue(self.local_id, group_key, attr_key)

    # -----------------------------------------------------------------------------------

    def OnEntityUpdateData(self, entity_id, data):
        # type: (str, dict) -> None
        """实体数据更新回调"""
        if entity_id not in self._entity_storage:
            self._entity_storage[entity_id] = {}
        storage = self._entity_storage[entity_id]  # type: dict
        storage.update(data)
        if entity_id in self._entity_update_recall:
            for recall in list(self._entity_update_recall[entity_id]):
                recall(data)

    # -----------------------------------------------------------------------------------

    def ModuleRequestSynEntityAttrEvent(self, args):
        # type: (dict) -> None
        """
        请求同步客户端实体属性\n
        - entityId: str
        - data: dict
        """
        entity_id = args["entityId"]
        data = args["data"]
        if entity_id not in self._entity_storage:
            self._entity_cache[entity_id] = data
            self.game_comp.AddTimer(0.1, lambda: self._entity_cache.pop(entity_id, None))
            return
        """
        回调注册更新:
        - 默认传入全部属性组数据
        """
        self.OnEntityUpdateData(entity_id, data)

    def AddEntityClientEvent(self, args):
        entity_id = args["id"]
        if not RawEntity.IsMob(entity_id):
            return
        if entity_id in self._entity_cache:
            data = self._entity_cache.pop(entity_id)
            self.OnEntityUpdateData(entity_id, data)
            return

        self._entity_storage[entity_id] = {}
        self.NotifyToServer(ModuleEvent.ModuleRequestEntityAttrEvent, {
            "playerId": self.local_id,
            "entityId": entity_id
        })

    def RemoveEntityClientEvent(self, args):
        entity_id = args["id"]
        self._entity_storage.pop(entity_id, None)
