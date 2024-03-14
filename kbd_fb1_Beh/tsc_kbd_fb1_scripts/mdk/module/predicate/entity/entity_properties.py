# -*- coding:utf-8 -*-


from predicate import EntityPredicate
from ..parts.base import ConditionBase


# 生物属性检测条件
class EntityPropertiesCondition(ConditionBase):
    """生物属性检测条件"""
    __mVersion__ = 1

    def Parse(self):
        entity = self.data["entity"]
        entity = self.GetContextValue(entity)
        if entity is None:
            return False
        return EntityPredicate(entity, self.data, self.context).GetResult()
