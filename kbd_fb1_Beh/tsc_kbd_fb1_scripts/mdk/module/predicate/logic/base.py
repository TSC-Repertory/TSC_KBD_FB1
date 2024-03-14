# -*- coding:utf-8 -*-


from ..parts.base import ConditionBase
from ..const import ModulePredicate


# 与集检测条件
class DefaultCondition(ConditionBase):
    """与集检测条件"""
    __mVersion__ = 1

    def Parse(self):
        for term in self.data["terms"]:
            assert isinstance(term, dict)
            if not self.mgr.Create(term, self.context).GetResult():
                return False
        return True


# 或集检测条件
class AlternativeCondition(ConditionBase):
    """或集检测条件"""
    __mVersion__ = 1

    def Parse(self):
        for term in self.data["terms"]:
            assert isinstance(term, dict)
            if self.mgr.Create(term, self.context).GetResult():
                return True
        return False


# 反转检测条件
class InvertedCondition(ConditionBase):
    """反转检测条件"""
    __mVersion__ = 1

    def Parse(self):
        term = self.data["term"]
        assert isinstance(term, dict)
        return not self.mgr.Create(term, self.context).GetResult()


# 引用检测条件
class ReferenceCondition(ConditionBase):
    """引用检测条件"""
    __mVersion__ = 1

    def Parse(self):
        name = self.data["name"]
        if name not in ModulePredicate.PredicateData:
            return False
        data = ModulePredicate.PredicateData[name]
        return self.mgr.Create(data, self.context).GetResult()
