# -*- coding:utf-8 -*-


from base import *
from image import CustomTipWindow


class UIModuleManagerPreset(UIPreset):
    """模块化管理UI预设界面"""
    __mVersion__ = 3

    def __init__(self, namespace, name, param):
        super(UIModuleManagerPreset, self).__init__(namespace, name, param)
        self._float_tip = None
        from button import ButtonRecallMgr
        self._recall_button = ButtonRecallMgr(self)

    def Create(self):
        float_tip = self.ConfigTipWindow()
        if float_tip:
            self._float_tip = CustomTipWindow(self, float_tip)
            self._float_tip.Display(True)
        super(UIModuleManagerPreset, self).Create()

    def OnDestroy(self):
        if isinstance(self._float_tip, CustomTipWindow):
            self._float_tip.OnDestroy()
            del self._float_tip
        self._recall_button.OnDestroy()
        del self._recall_button
        super(UIModuleManagerPreset, self).OnDestroy()

    # -----------------------------------------------------------------------------------

    def ConfigTipWindow(self):
        """配置浮窗"""
        return ""

    # -----------------------------------------------------------------------------------

    def SetButtonBind(self, comp, recall, method=TouchEvent.TouchUp, swallow=True):
        return self._recall_button.SetButtonBind(comp, recall, method, swallow)

    # -----------------------------------------------------------------------------------

    def SetUITips(self, msg):
        # type: (str) -> None
        """设置UI提示"""
        if isinstance(self._float_tip, CustomTipWindow):
            self._float_tip.SetValue(msg)

    def SetUITipsPos(self, pos):
        # type: (tuple) -> None
        """设置UI提示窗位置"""
        if isinstance(self._float_tip, CustomTipWindow):
            self._float_tip.SetFixPos(pos)

    def SetUITipsDuration(self, duration):
        # type: (int) -> None
        """
        设置UI提示窗显示时长\n
        - default: 15
        """
        if isinstance(self._float_tip, CustomTipWindow):
            self._float_tip.SetDuration(int(duration))

    def GetUITips(self):
        # type: () -> CustomTipWindow
        """获得提示窗实例"""
        return self._float_tip

    def ResetUITipPos(self):
        """重置显示位置"""
        if isinstance(self._float_tip, CustomTipWindow):
            self._float_tip.ResetFixPos()


class UIModuleSubPagePreset(UIModuleBase):
    """模块化管理UI预设子界面"""
    __mVersion__ = 1

    def __init__(self, mgr, **kwargs):
        self.mgr = weakref.proxy(mgr)  # type: UIModuleManagerPreset
        super(UIModuleSubPagePreset, self).__init__(mgr.ui_node, **kwargs)

    def OnDestroy(self):
        del self.mgr
        super(UIModuleSubPagePreset, self).OnDestroy()

    # -----------------------------------------------------------------------------------

    def SetButtonBind(self, comp, recall, method=TouchEvent.TouchUp):
        return self.mgr.SetButtonBind(comp, recall, method)
