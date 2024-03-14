# -*- coding:utf-8 -*-


from const import *
from ..system.preset import *


class ShopModuleServer(LoadConfigModuleServer):
    """商店模块服务端"""
    __mVersion__ = 1
    __identifier__ = ModuleEnum.identifier
    _ModuleRequestRegisterEvent = ModuleEvent.ModuleRequestShopRegisterEvent

    def ConfigEvent(self):
        super(ShopModuleServer, self).ConfigEvent()

    def OnLoadModConfig(self, data):
        ModuleShop.ShopData = data
