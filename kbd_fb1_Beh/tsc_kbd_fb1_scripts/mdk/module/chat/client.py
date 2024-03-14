# -*- coding:utf-8 -*-


from const import *
from ..system.base import *


class ChatModuleClient(ModuleClientBase):
    """聊天模块客户端"""
    __mVersion__ = 2
    __identifier__ = ModuleEnum.identifier

    def ConfigEvent(self):
        super(ChatModuleClient, self).ConfigEvent()
        self.defaultEvent.update({
            ClientEvent.UiInitFinished: self.UiInitFinished
        })

    # -----------------------------------------------------------------------------------

    def UiInitFinished(self, _):
        clientApi.SetHudChatStackVisible(False)
        self.RegisterUI(ModuleUI.chat_key, ModuleUI.chat_config)
        self.CreateUI(ModuleUI.chat_key)
