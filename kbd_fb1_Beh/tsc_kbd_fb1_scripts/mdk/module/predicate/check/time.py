# -*- coding:utf-8 -*-


from ..parts.base import ConditionBase


# 时间检测条件
class TimeCheckCondition(ConditionBase):
    """时间检测条件"""
    __mVersion__ = 1

    def Parse(self):
        dim_comp = self.comp_factory.CreateDimension(self.predicate_id)

        value = self.data["value"]
        period = self.data.get("period")

        dim_id = dim_comp.GetEntityDimensionId()
        dim_time = dim_comp.GetLocalTime(dim_id)

        return self.TestValue(value, dim_time)
