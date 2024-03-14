# -*- coding:utf-8 -*-



class ModuleEnum(object):
    """模块枚举"""
    identifier = "render"
    parser_identifier = "render"


class ModuleEvent(object):
    """模块事件"""
    ModuleRequestRenderRegisterEvent = "ModuleRequestRenderRegisterEvent"
    ModuleRequestSynRenderDataEvent = "ModuleRequestSynRenderDataEvent"


class ModuleRender(object):
    """模块渲染"""
    GlobalRenderData = {}
    PlayerRenderData = {}
    MobRenderData = {}
