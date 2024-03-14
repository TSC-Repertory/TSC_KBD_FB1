# -*- coding:utf-8 -*-


from ...loader import MDKConfig


class ModuleEnum(object):
    """模块枚举"""
    identifier = "chat"


class ModuleEvent(object):
    """模块事件"""
    ModuleRequestDisplayChatEvent = "ModuleRequestDisplayChatEvent"


class ModuleUI(object):
    """模组UI"""
    chat_key = "preset_chat"
    chat_cls = ".".join((MDKConfig.ModuleRoot, ModuleEnum.identifier, "ui", "ChatUI"))
    chat_namespace = "preset_chat.chat_screen"
    chat_config = (MDKConfig.ModuleNamespace, chat_key, chat_cls, chat_namespace)
