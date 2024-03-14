# -*- coding:utf-8 -*-


from ...loader import MDKConfig


class ModuleEnum(object):
    """模块枚举"""
    identifier = "debug"


class ModuleUI(object):
    """模组UI"""
    debug_key = "preset_debug"
    debug_cls = ".".join((MDKConfig.ModuleRoot, ModuleEnum.identifier, "ui", "root", "DebugScreen"))
    debug_name_space = "%s.debug_screen" % debug_key
    debug_config = (MDKConfig.ModuleNamespace, debug_key, debug_cls, debug_name_space)


class ModuleEvent(object):
    """模块事件"""
    RequestDisplayRegisterMolangEvent = "RequestDisplayRegisterMolangEvent"  # 请求显示注册molang事件
    # 生物控制
    ModuleRequestUpdateFocusEntityEvent = "ModuleRequestUpdateFocusEntityEvent"
