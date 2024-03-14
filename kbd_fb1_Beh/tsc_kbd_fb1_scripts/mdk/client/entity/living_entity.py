# -*- coding:utf-8 -*-


from entity import Entity


class LivingEntity(Entity):
    """客户端生物基类"""
    __mVersion__ = 3

    def __init__(self, entityId):
        super(LivingEntity, self).__init__(entityId)
        self._mod_storage = {}

    # -----------------------------------------------------------------------------------

    @property
    def health(self):
        """获取目前生命"""
        return self.query_comp.GetMolangValue("query.health")

    @property
    def max_health(self):
        """获取最大生命"""
        return self.query_comp.GetMolangValue("query.max_health")

    # -----------------------------------------------------------------------------------

    def GetRateHealth(self):
        """
        生命当前值比最大值\n
        - 常用于UI显示
        """
        return float(self.health) / self.max_health

    # ---------------------

    def SetStorage(self, key, storage):
        # type: (str, dict) -> None
        """
        设置模组数据缓存\n
        - 不会存于客户端本地
        """
        self._mod_storage[key] = storage

    def GetStorage(self, key):
        # type: (str) -> dict
        """
        获得模组数据缓存\n
        - 需要服务端同步
        """
        storage = self._mod_storage.get(key, {})
        if not storage:
            return {}
        return storage
