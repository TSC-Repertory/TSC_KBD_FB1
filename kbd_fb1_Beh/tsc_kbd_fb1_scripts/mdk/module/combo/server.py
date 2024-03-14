# -*- coding:utf-8 -*-


from const import *
from ..system.base import *


class ComboModuleServer(ModuleServerBase):
    """连招模块服务端"""
    __identifier__ = ModuleEnum.identifier
    __mVersion__ = 3

    def __init__(self):
        super(ComboModuleServer, self).__init__()
        self.BroadcastEvent(ModuleEvent.OnFinishedInitComboModuleEvent, {})

    def ConfigEvent(self):
        super(ComboModuleServer, self).ConfigEvent()
        self.clientEvent[ModuleEvent.OnClientFinishedComboEvent] = self.OnClientFinishedComboEvent

    # -----------------------------------------------------------------------------------

    def OnClientFinishedComboEvent(self, args):
        # type: (dict) -> None
        """客户端完成连招事件"""
        if not args.get("cancel"):
            self.BroadcastToAllClient(ModuleEvent.ServerSynchronizeComboEvent, args)
