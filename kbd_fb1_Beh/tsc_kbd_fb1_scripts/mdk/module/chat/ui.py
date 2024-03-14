# -*- coding:utf-8 -*-


from const import ModuleEvent
from ...ui.system.preset import UIPreset


class ChatUI(UIPreset):
    """聊天UI"""
    __mVersion__ = 1

    def __init__(self, namespace, name, param):
        super(ChatUI, self).__init__(namespace, name, param)
        self.parent_path = None
        self.mould_path = None
        self.chat_storage = {}

        self.chat_index = 0
        self.scroll_control = None

        self.display_duration = 300  # 10s
        self.display_fade_out = 30  # 1s

    def ConfigEvent(self):
        super(ChatUI, self).ConfigEvent()
        self.serverEvent[ModuleEvent.ModuleRequestDisplayChatEvent] = self.ModuleRequestDisplayChatEvent

    def Create(self):
        super(ChatUI, self).Create()
        self.scroll_control = self.GetScrollViewUIControl("/panel_chat/scroll_view")
        self.parent_path = self.scroll_control.GetScrollViewContentPath()
        self.mould_path = self.parent_path + "/mould"

    # -----------------------------------------------------------------------------------

    def Update(self):
        if self.chat_storage:
            for path, cd in self.chat_storage.items():
                cd -= 1
                self.chat_storage[path] = cd
                if cd <= 0:
                    self.SetChatFade(path, cd)

    def CreateNewChat(self, context):
        # type: (str) -> None
        """创建新的对话"""
        self.chat_index += 1
        chat = self.CloneComp(self.mould_path, self.parent_path, "chat%s" % self.chat_index)
        label = chat + "/image/label"
        self.SetLabelText(label, context)
        image = chat + "/image"
        # alpha control
        self.SetVisible(chat, True)
        self.chat_storage[chat] = self.display_duration
        self.scroll_control.SetScrollViewPercentValue(100)

    def SetChatFade(self, path, index):
        # type: (str, int) -> None
        """聊天信息渐变消失"""
        opacity = (1.0 - index) / self.display_fade_out
        self.SetOpacity(path, opacity)
        self.SetOpacity(path + "/image/label", opacity)
        if opacity >= 1:
            self.chat_storage.pop(path, None)
            self.DelComp(path)

    # -----------------------------------------------------------------------------------

    def ModuleRequestDisplayChatEvent(self, args):
        context = args["context"]
        self.CreateNewChat(context)
