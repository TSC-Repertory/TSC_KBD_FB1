# -*- coding:utf-8 -*-


from const import *
from ..system.base import *


class ChatModuleServer(ModuleServerBase):
    """聊天模块服务端"""
    __mVersion__ = 2
    __identifier__ = ModuleEnum.identifier

    def ConfigEvent(self):
        super(ChatModuleServer, self).ConfigEvent()
        self.defaultEvent.update({
            ServerEvent.ServerChatEvent: self.ServerChatEvent
        })

        # -----------------------------------------------------------------------------------

    def ServerChatEvent(self, args):
        username = args["username"]
        message = args["message"]
        context = "<%s> %s" % (username, message)
        self.BroadcastToAllClient(ModuleEvent.ModuleRequestDisplayChatEvent, {"context": context})
