# -*- coding:utf-8 -*-


from base import UIModuleBase
from ..system.preset import *


class SliderMgr(UIModuleBase):
    """自定义滑动条"""
    __mVersion__ = 2

    def __init__(self, ui_node, path, **kwargs):
        super(SliderMgr, self).__init__(ui_node, **kwargs)
        self.path = path
        self.slider = self.GetButtonUIControl(path)

        self.rate = 0
        self.maxValue = 1

        # 边缘修正
        self.modifyRate = 0.8

        # 拖动回调
        self.dragCallback = None
        # 取消拖动回调
        self.cancelCallback = None
        # 用于获得边缘
        self.parentPath = self.GetParentPath(path)
        self.parentComp = self.GetBaseUIControl(self.parentPath)

        # 拖动绑定
        self.SetButtonBind(path, self._OnSliderPressed, TouchEvent.TouchDown)
        self.SetButtonBind(path, self._OnSliderPressed, TouchEvent.TouchMove)
        self.SetButtonBind(path, self._OnSliderCancel, TouchEvent.TouchCancel)

    def OnDestroy(self):
        del self.slider
        del self.parentComp
        super(SliderMgr, self).OnDestroy()

    # -----------------------------------------------------------------------------------

    def ConfigDragActiveRecall(self, recall):
        # type: (any) -> bool
        """设置拖动回调"""
        if callable(recall):
            self.dragCallback = recall
            return True
        return False

    def ConfigDragCancelRecall(self, recall):
        # type: (any) -> bool
        """设置拖动取消回调"""
        if callable(recall):
            self.cancelCallback = recall
            return True
        return False

    # -----------------------------------------------------------------------------------

    def SetMaxValue(self, value):
        # type: (int) -> None
        """设置滑块最大值"""
        self.maxValue = value

    def SetRate(self, rate):
        # type: (float) -> None
        """设置滑块百分比位置"""
        self.rate = Misc.GetClamp(rate, 0, 1)

        winSize = self.parentComp.GetSize()
        compPos, compSize = self.slider.GetPosition(), self.slider.GetSize()

        rightMax = winSize[0] - compSize[0]
        newX = self.rate * rightMax

        compPos = (newX, compPos[1])
        self.slider.SetPosition(compPos)

        self._OnDragCallback()

    def GetRate(self):
        """获取目前的滑块百分比"""
        return self.rate

    def GetValue(self):
        # type: () -> int
        """获取目前的滑块值"""
        return int(Misc.GetClamp(math.ceil(self.rate * self.maxValue), 0, self.maxValue))

    def AddValue(self):
        """加值"""
        preValue = int(self.maxValue * self.rate)
        newRate = float(Misc.GetClamp(preValue + 1, 0, self.maxValue)) / self.maxValue
        self.SetRate(newRate)

    def DelValue(self):
        """减值"""
        preValue = int(self.maxValue * self.rate)
        newRate = float(Misc.GetClamp(preValue - 1, 0, self.maxValue)) / self.maxValue
        self.SetRate(newRate)

    # -----------------------------------------------------------------------------------

    def _OnSliderPressed(self, args):
        """按住按钮"""
        fullPos = self.GetFullPos(self.parentPath)

        winSize = self.parentComp.GetSize()
        compPos, compSize = self.slider.GetPosition(), self.slider.GetSize()
        rightMax = fullPos[0] + winSize[0]
        prePosX = args["TouchPosX"]
        newPosX = Misc.GetClamp(prePosX, fullPos[0], rightMax) - fullPos[0]

        self.rate = newPosX / winSize[0]
        self.GetProgressBarUIControl(self.parentPath).SetValue(self.rate)

        # 居中修正
        newPosX -= compSize[0] / 2
        self.slider.SetPosition((newPosX, compPos[1]))

        # 拖动回调
        self._OnDragCallback()

    def _OnSliderCancel(self, _):
        """取消按住"""
        if callable(self.cancelCallback):
            self.cancelCallback(self)
            return

    def _OnDragCallback(self):
        """按住回调"""
        if callable(self.dragCallback):
            self.dragCallback(self)
