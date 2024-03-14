# -*- coding:utf-8 -*-


import random

from ..parts.base import ConditionBase


# 随机检测条件
class RandomChanceCondition(ConditionBase):
    """随机检测条件"""
    __mVersion__ = 1

    def Parse(self):
        return random.random() <= self.data["chance"]
