# -*- coding:utf-8 -*-


from const import *
from parts.mgr import PredicateMgr
from ..system.preset import LoadConfigModuleServer


class PredicateModuleServer(LoadConfigModuleServer):
    """断言模块服务端"""
    __mVersion__ = 1
    __identifier__ = ModuleEnum.identifier
    _ModuleRequestRegisterEvent = ModuleEvent.ModuleRequestPredicateRegisterEvent

    def __init__(self):
        super(PredicateModuleServer, self).__init__()
        self.predicate_mgr = PredicateMgr.GetInstance()

    def GetDefaultConfig(self):
        return ["predicate/root.json"]

    def OnLoadModConfig(self, data):
        ModulePredicate.PredicateData = data
        return True

    @staticmethod
    def GetPredicateConfig():
        # type: () -> dict
        """获得断言配置"""
        return ModulePredicate.PredicateData

    def ParsePredicate(self, predicate, context=None):
        # type: (str, dict) -> bool
        """解析断言"""
        if predicate not in ModulePredicate.PredicateData:
            print "[warn]", "Invalid predicate: %s" % predicate
            return False
        data = ModulePredicate.PredicateData[predicate]
        return self.predicate_mgr.Create(data, context).GetResult()

    def GetPredicateMgr(self):
        # type: () -> PredicateMgr
        return self.predicate_mgr
