# -*- coding:utf-8 -*-


from predicate import DamagePredicate
from ..parts.base import ConditionBase


# 伤害源检测条件
class DamageSourcePropertiesCondition(ConditionBase):
    """伤害源检测条件"""
    __mVersion__ = 1

    def Parse(self):
        predicate = self.data["predicate"]  # 伤害类型共通标签
        return DamagePredicate(predicate, self.context).GetResult()
