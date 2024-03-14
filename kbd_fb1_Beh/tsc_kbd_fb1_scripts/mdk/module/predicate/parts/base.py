# -*- coding:utf-8 -*-


import weakref

import mod.server.extraServerApi as serverApi

from ..const import ConditionEnum


# 断言基类
class PredicateBase(object):
    """断言基类"""
    __mVersion__ = 3

    def __init__(self, data, context):
        self.comp_factory = serverApi.GetEngineCompFactory()
        self.data = data  # type: dict
        self.context = context  # type: dict

        # 是否通过
        self.is_pass = None

        # 断言实体
        self.predicate_id = self.context["this"]
        # 断言位置
        self.predicate_pos = self.context.get("position", self.comp_factory.CreatePos(self.predicate_id).GetFootPos())
        # 断言维度
        self.predicate_dim = self.comp_factory.CreateDimension(self.predicate_id).GetEntityDimensionId()

    def __del__(self):
        print "[warn]", "del: %s" % self.__class__.__name__

    def Parse(self):
        # type: () -> bool
        """解析断言"""

    def GetResult(self):
        # type: () -> bool
        """获得断言结果"""
        if self.is_pass is None:
            self.is_pass = self.Parse()
        return self.is_pass

    def GetContextValue(self, target):
        # type: (str) -> any
        """获得上下文值"""
        if target not in self.context:
            print "[warn]", "Invalid context value: %s" % target
            return None
        return self.context[target]

    @staticmethod
    def TestValue(value, target):
        # type: (any, any) -> bool
        """测试值"""
        if isinstance(value, dict):
            return target["min"] <= value <= target["max"]
        else:
            return value == target


# 条件基类
class ConditionBase(PredicateBase):
    """条件基类"""
    __mVersion__ = 3

    def __init__(self, data, context):
        super(ConditionBase, self).__init__(data, context)
        from mgr import PredicateMgr
        self.mgr = PredicateMgr.GetInstance()

        # 是否丢弃
        self.is_discard = False

        self.condition_type = data["condition"]
        if self.condition_type not in ConditionEnum.Available_Key:
            print "[warn]", "Invalid key: %s" % self.condition_type
            self.is_discard = True

    def GetResult(self):
        # type: () -> bool
        """获得条件是否通过"""
        if self.is_discard:
            return False
        return super(ConditionBase, self).GetResult()
