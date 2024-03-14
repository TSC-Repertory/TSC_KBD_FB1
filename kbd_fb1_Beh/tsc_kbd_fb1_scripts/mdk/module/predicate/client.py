# -*- coding:utf-8 -*-


from const import *
from parser import PredicateParser
from ..system.base import *


class PredicateModuleClient(ModuleClientBase):
    """断言模块客户端"""
    __mVersion__ = 1
    __identifier__ = ModuleEnum.identifier

    def __init__(self):
        super(PredicateModuleClient, self).__init__()
        self.ModuleSystem.SetModConfigParser(PredicateParser)
