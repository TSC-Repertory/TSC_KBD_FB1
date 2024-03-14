# -*- coding:utf-8 -*-


from const import *
from parser import *
from ..system.base import *


class ItemModuleClient(ModuleClientBase):
    """物品模块客户端"""
    __mVersion__ = 2
    __identifier__ = ModuleEnum.identifier

    def __init__(self):
        super(ItemModuleClient, self).__init__()
        self.ModuleSystem.SetModConfigParser(ItemFoodConsumeParser)
        self.ModuleSystem.SetModConfigParser(ItemRecipeCraftParser)
