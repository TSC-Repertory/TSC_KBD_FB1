# -*- coding:utf-8 -*-


from const import *
from ..system.base import *


class ShopModuleClient(ModuleClientBase):
    """商店模块客户端"""
    __mVersion__ = 2
    __identifier__ = ModuleEnum.identifier

    def ConfigEvent(self):
        super(ShopModuleClient, self).ConfigEvent()
        self.defaultEvent.update({
            ClientEvent.UiInitFinished: self.UiInitFinished
        })

        # -----------------------------------------------------------------------------------

    def UiInitFinished(self, _):
        """注册UI配置"""
        self.RegisterUI(ModulePresetUI.shop_key, ModulePresetUI.shop_config)
