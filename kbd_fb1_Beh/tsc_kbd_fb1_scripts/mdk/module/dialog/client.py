# -*- coding:utf-8 -*-


from const import *
from parser import *
from ...module.system.base import *


class DialogModuleClient(ModuleClientBase):
    """对话模块客户端"""
    __mVersion__ = 3
    __identifier__ = ModuleEnum.identifier

    def __init__(self):
        super(DialogModuleClient, self).__init__()
        self.system.SetModConfigParser(DialogParser())

    def ConfigEvent(self):
        super(DialogModuleClient, self).ConfigEvent()
        self.serverEvent.update({
            ModuleEvent.ModuleRequestSynDialogDataEvent: self.ModuleRequestSynDialogDataEvent
        })
        self.clientEvent.update({
            ModuleEvent.RequestDialogDataEvent: self.RequestDialogDataEvent
        })

        # -----------------------------------------------------------------------------------

    @classmethod
    def ModuleRequestSynDialogDataEvent(cls, args):
        data = args["data"]
        ModuleDialog.DialogData = data

    def RequestDialogDataEvent(self, args):
        dialogId = args["dialogId"]
