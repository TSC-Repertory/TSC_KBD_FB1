# -*- coding:utf-8 -*-



class ModuleEnum(object):
    """模块枚举"""
    identifier = "combo"


class ModuleEvent(object):
    """模块事件"""
    OnFinishedInitComboModuleEvent = "OnFinishedInitComboModuleEvent"  # 完成初始化事件

    """配置事件"""
    ModuleRequestLoadComboConfigEvent = "ModuleRequestLoadComboConfigEvent"  # 请求载入连招配置事件

    ServerSynchronizeComboEvent = "ServerSynchronizeComboEvent"
    OnClientFinishedComboEvent = "OnClientFinishedComboEvent"
    ClientActiveComboEvent = "ClientActiveComboEvent"
