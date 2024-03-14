# -*- coding:utf-8 -*-



class ModuleEnum(object):
    """模块枚举"""
    identifier = "block"


class ModuleEvent(object):
    """模块事件"""
    ModuleRequestBlockClassMapEvent = "ModuleRequestBlockClassMapEvent"
    ModuleRequestShuntDownBlockEvent = "ModuleRequestShuntDownBlockEvent"
    ModuleOnBlockAddPlayerEvent = "ModuleOnBlockAddPlayerEvent"
