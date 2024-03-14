# -*- coding:utf-8 -*-



class ModuleEnum(object):
    """模块枚举"""
    identifier = "indicator"


class ModuleEvent(object):
    """模块事件"""
    ModuleRequestHideEngineTypeHpBarEvent = "ModuleRequestHideEngineTypeHpBarEvent"  # 请求隐藏血条配置
    RequestDisplayDamageIndicatorEvent = "RequestDisplayDamageIndicatorEvent"  # 请求伤害显示
