# -*- coding:utf-8 -*-


from .....ui.module.base import *
from .....ui.module.button import ButtonRecallMgr


class LogicBlockUIBase(UIPreset):
    """逻辑方块界面基类"""
    __mVersion__ = 1

    def __init__(self, namespace, name, param):
        super(LogicBlockUIBase, self).__init__(namespace, name, param)
        self._recall_mgr = ButtonRecallMgr(self)

    def OnDestroy(self):
        self._recall_mgr.OnDestroy()
        del self._recall_mgr
        super(LogicBlockUIBase, self).OnDestroy()

    # -----------------------------------------------------------------------------------

    def SetButtonBind(self, comp, recall, method=TouchEvent.TouchUp, swallow=True):
        return self._recall_mgr.SetButtonBind(comp, recall, method, swallow)

    def SetExitUI(self):
        """
        关闭界面\n
        - 执行退出操作时调用该接口
        """
