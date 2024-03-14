# -*- coding:utf-8 -*-


from ...interface.data.base import StorageBase


class ModuleEnum(object):
    """模块枚举"""
    identifier = "dialog"


class ModuleEvent(object):
    """模块事件"""
    ModuleRequestDialogRegisterEvent = "ModuleRequestDialogRegisterEvent"  # 请求注册配置事件
    ModuleRequestSynDialogDataEvent = "ModuleRequestSynDialogDataEvent"  # 同步对话数据事件
    # -----------------------------------------------------------------------------------
    RequestDialogDataEvent = "RequestDialogDataEvent"


class ModuleDialog(StorageBase):
    """模块对话"""
    DialogData = {}

    @classmethod
    def HasData(cls, dialog):
        # type: (str) -> bool
        return dialog in cls.DialogData

    @classmethod
    def GetData(cls, dialog):
        # type: (str) -> dict
        config = cls.DialogData.get(dialog, {})
        return config
