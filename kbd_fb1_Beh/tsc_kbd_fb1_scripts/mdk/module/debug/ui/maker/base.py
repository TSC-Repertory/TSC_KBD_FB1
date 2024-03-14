# -*- coding:utf-8 -*-


import weakref
from functools import wraps

from .....common.utils.misc import Misc
from .....ui.module import *

if __name__ == '__main__':
    from ...ui.root import DebugScreen


def check_active(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        screen = args[0]  # type: MakerScreenBase
        if not screen.IsActive():
            return
        func(*args, **kwargs)

    return wrapped


class MakerScreenBase(UIModuleBase):
    """技能制造界面"""
    __mVersion__ = 1

    def __init__(self, ui_node, **kwargs):
        super(MakerScreenBase, self).__init__(ui_node, **kwargs)
        self.ui_node = ui_node  # type: DebugScreen
        self.button_mgr = ButtonRecallMgr(self.ui_node)
        self.node_storage = {}  # key: WinNode

    def OnDestroy(self):
        for node in self.node_storage.values():
            node.OnDestroy()
        del self.node_storage
        self.button_mgr.OnDestroy()
        del self.button_mgr
        super(MakerScreenBase, self).OnDestroy()

    def ConfigEvent(self):
        super(MakerScreenBase, self).ConfigEvent()
        self.defaultEvent.update({
            ClientEvent.MouseWheelClientEvent: self.MouseWheelClientEvent,
            ClientEvent.TapBeforeClientEvent: self.TapBeforeClientEvent,
        })

    def SetButtonBind(self, comp, recall, method=TouchEvent.TouchUp):
        self.button_mgr.SetButtonBind(comp, recall, method)

    def AddWinNode(self, path, node):
        # type: (str, WinNode) -> None
        """添加结点"""
        self.node_storage[path] = node

    def DelWinNode(self, path):
        """删除结点"""
        node = self.node_storage.pop(path, None)  # type: WinNode
        if node:
            self.DelComp(path)
            node.OnDestroy()


class WinNode(UIModuleSubPagePreset):
    """窗口结点"""
    __mVersion__ = 1

    def __init__(self, mgr, path, node_type, **kwargs):
        super(WinNode, self).__init__(mgr, **kwargs)
        self.mgr = weakref.proxy(mgr)  # type: MakerScreenBase
        self.root = path
        self.drag_cache = {}
        self.win_comp = self.GetBaseUIControl(self.root)
        self.win_comp.SetVisible(True)
        self.win_comp.SetPosition(Misc.GetPosModify(clientApi.GetTouchPos(), (0, -20)))
        self.bind_set = set()

        # 设置结点类型
        self.node_type = node_type

    def OnDestroy(self):
        del self.drag_cache
        del self.win_comp
        for path in list(self.bind_set):
            self.mgr.button_mgr.DestroyCompBind(path)
        super(WinNode, self).OnDestroy()

    def Create(self):
        path = self.root + "/title/discard"
        self.SetButtonBind(path, self.KeyRecallDiscardNode)

        path = self.root + "/drag"
        self.SetButtonBind(path, self.KeyRecallDragWinActive, TouchEvent.TouchMove)
        self.SetButtonBind(path, self.KeyRecallDragWinCancel, TouchEvent.TouchCancel)
        self.SetButtonBind(path, self.KeyRecallDragWinCancel, TouchEvent.TouchUp)

    # -----------------------------------------------------------------------------------

    def KeyRecallDiscardNode(self, _):
        """删除结点"""
        self.mgr.DelWinNode(self.root)

    def KeyRecallDragWinActive(self, args):
        path = args["ButtonPath"]  # type: str
        touch_pos = (args["TouchPosX"], args["TouchPosY"])
        if path not in self.drag_cache:
            comp_pos = self.win_comp.GetPosition()
            self.drag_cache[path] = Misc.GetPosModify(touch_pos, comp_pos, method="sub")
        self.win_comp.SetPosition(Misc.GetPosModify(touch_pos, self.drag_cache[path], method="sub"))

    def KeyRecallDragWinCancel(self, args):
        path = args["ButtonPath"]  # type: str
        self.drag_cache.pop(path, None)

    # -----------------------------------------------------------------------------------

    def SetButtonBind(self, comp, recall, method=TouchEvent.TouchUp):
        self.bind_set.add(comp)
        return super(WinNode, self).SetButtonBind(comp, recall, method)
