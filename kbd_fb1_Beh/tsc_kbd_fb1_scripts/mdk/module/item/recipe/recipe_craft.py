# -*- coding:utf-8 -*-


from ..common.base import *
from ..const import ModuleEnum, ModuleEvent


class ItemRecipeCraftModuleServer(LoadConfigModuleServer):
    """物品配方合成模块服务端"""
    __mVersion__ = 1
    __identifier__ = ModuleEnum.recipe_craft
    _ModuleRequestRegisterEvent = ModuleEvent.ModuleRequestItemRecipeCraftRegisterEvent
    _data_config = {
        "storage_key": "ItemRecipeCraftStorage",  # 数据键
        "syn_data_key": ""  # 同步数据键 - 客户端缓存
    }
