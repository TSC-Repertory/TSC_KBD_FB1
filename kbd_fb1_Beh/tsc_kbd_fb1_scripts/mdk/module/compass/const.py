# -*- coding:utf-8 -*-


from ...loader import MDKConfig


class ModuleEnum(object):
    """模块枚举"""
    identifier = "compass"


class ModuleEvent(object):
    """模块事件"""


class ModuleUI(object):
    """模块界面"""
    ui_cls = "%s.mdk.module.%s.ui.CompassScreen" % (MDKConfig.GetScriptDir(), ModuleEnum.identifier)
