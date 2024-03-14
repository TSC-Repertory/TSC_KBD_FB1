# -*- coding:utf-8 -*-


from base import ConditionBase
from ..block import *
from ..check import *
from ..const import ConditionEnum
from ..entity import *
from ..logic import *


# 断言管理
class PredicateMgr(object):
    """条件管理"""
    __mVersion__ = 1
    _instance = None

    def __new__(cls):
        if cls._instance:
            return cls._instance
        cls._instance = super(PredicateMgr, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super(PredicateMgr, self).__init__()
        self.condition_map = {
            ConditionEnum.default: DefaultCondition,
            ConditionEnum.alternative: AlternativeCondition,
            ConditionEnum.inverted: InvertedCondition,
            ConditionEnum.reference: ReferenceCondition,

            ConditionEnum.entity_properties: EntityPropertiesCondition,
            ConditionEnum.block_state_property: BlockStatePropertyCondition,
            ConditionEnum.damage_source_properties: DamageSourcePropertiesCondition,

            ConditionEnum.location_check: LocationCheckCondition,
            ConditionEnum.time_check: TimeCheckCondition,
            ConditionEnum.weather_check: WeatherCheckCondition,

            ConditionEnum.match_tool: MatchToolCondition,
            ConditionEnum.random_chance: RandomChanceCondition,
        }

    @classmethod
    def GetInstance(cls):
        """获得单例"""
        if cls._instance:
            return cls._instance
        return PredicateMgr()

    # -----------------------------------------------------------------------------------

    def Create(self, data, context):
        # type: (dict, dict) -> ConditionBase
        """创建条件实例"""
        condition_type = data["condition"]
        condition_cls = self.condition_map.get(condition_type)
        if not condition_cls:
            return ConditionBase(data, context)
        return condition_cls(data, context)
