# -*- coding:utf-8 -*-


from ...loader import MDKConfig


class ModuleEnum(object):
    """模块枚举"""
    identifier = "infection.shop"


class ModuleEvent(object):
    """模块事件"""
    ModuleRequestShopRegisterEvent = "ModuleRequestShopRegisterEvent"


class ModuleShop(object):
    """模块商店配置"""
    ShopData = {}


class ModulePresetUI(object):
    """模块预设界面"""
    shop_key = "uiComponent"
    shop_cls = ".".join((MDKConfig.ModuleRoot, ModuleEnum.identifier, "ui.preset", "ShopModuleUIPreset"))
    shop_namespace = "uiComponent.shop_screen"
    shop_config = (MDKConfig.ModuleNamespace, shop_key, shop_cls, shop_namespace)
