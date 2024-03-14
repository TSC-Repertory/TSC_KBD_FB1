# -*- coding:utf-8 -*-


from ..block.predicate import LocationPredicate
from ..parts.base import ConditionBase


# 位置检测条件
class LocationCheckCondition(ConditionBase):
    """位置检测条件"""
    __mVersion__ = 1

    def Parse(self):
        predicate = self.data["predicate"]
        offset_x = self.data.get("offsetX", 0)
        offset_y = self.data.get("offsetY", 0)
        offset_z = self.data.get("offsetZ", 0)
        offset = (offset_x, offset_y, offset_z)

        check_pos = tuple(map(lambda x, y: x - y, self.predicate_pos, offset))
        return LocationPredicate(check_pos, predicate, self.context).GetResult()
