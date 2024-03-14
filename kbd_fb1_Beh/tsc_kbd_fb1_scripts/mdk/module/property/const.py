# -*- coding:utf-8 -*-



class ModuleEnum(object):
    """模块枚举"""
    identifier = "property"


class ModuleEvent(object):
    """模块事件"""
    """只读事件"""
    OnPlayerJumpEvent = "OnPlayerJumpEvent"
    # -----------------------------------------------------------------------------------
    """配置事件"""
    ModuleRequestLoadMolangConfigEvent = "ModuleRequestLoadMolangConfigEvent"  # 请求载入molang配置事件
    # -----------------------------------------------------------------------------------
    ModRequestGetPlayerNameEvent = "ModRequestGetPlayerNameEvent"  # 请求目标名字事件
    ModResponsePlayerNameEvent = "ModResponsePlayerNameEvent"  # 响应请求目标名字事件
    RequestTargetMolangEvent = "RequestTargetMolangEvent"  # 请求目标molang事件
    RequestPlayerMolangEvent = "RequestPlayerMolangEvent"  # 请求客户端molang事件
    ResponsePlayerMolangEvent = "ResponsePlayerMolangEvent"  # 响应服务端molang请求事件

    RequestDisplayRegisterMolangEvent = "RequestDisplayRegisterMolangEvent"
