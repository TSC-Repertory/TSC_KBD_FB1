# -*- coding:utf-8 -*-



class ModuleEnum(object):
    """模块枚举"""
    identifier = "attribute"


class ModuleEvent(object):
    """模块事件"""
    ModuleRequestAttributeRegisterEvent = "ModuleRequestAttributeRegisterEvent"  # 请求注册配置事件
    ModuleRequestEntityAttrEvent = "ModuleRequestEntityAttrEvent"  # 请求实体数据事件
    ModuleRequestSynEntityAttrEvent = "ModuleRequestSynEntityAttrEvent"  # 请求同步客户端实体属性


class ModuleConfig(object):
    """模块配置"""
    GroupDefine = {}
    AttrDefine = {}
    TableDefine = {}
