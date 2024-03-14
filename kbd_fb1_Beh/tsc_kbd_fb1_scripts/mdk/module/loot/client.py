# -*- coding:utf-8 -*-


from const import *
from parser import *
from ..system.base import *


class LootModuleClient(ModuleClientBase):
    """战利品模块客户端"""
    __mVersion__ = 2
    __identifier__ = ModuleEnum.identifier

    def __init__(self):
        super(LootModuleClient, self).__init__()
        self.system.SetModConfigParser(LootParser())
        self.system.SetModConfigParser(VanillaLoot())
