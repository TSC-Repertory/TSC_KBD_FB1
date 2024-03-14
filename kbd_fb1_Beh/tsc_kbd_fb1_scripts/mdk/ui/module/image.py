# -*- coding:utf-8 -*-


from base import UIModuleBase
from ..system.preset import *


class CustomTipWindow(UIModuleBase):
    """浮窗控制"""
    __mVersion__ = 4

    def __init__(self, ui_node, image, label=None, **kwargs):
        kwargs["manual_listen"] = True
        super(CustomTipWindow, self).__init__(ui_node, **kwargs)
        if not label:
            label = image + "/label"
        # -----------------------------------------------------------------------------------
        self._parent = self.GetParentPath(image)
        self._image = image
        self._label = label
        self._context = ""
        self._fade_in = 15
        self._fade_out = 15
        self._duration = 20
        self._move_range = (0.99, 0.90)
        self._gen = None
        self._tick = 0
        self._fix_pos = None
        # -----------------------------------------------------------------------------------
        self.SetActive(False)

    def OnDestroy(self):
        if self.IsActive():
            self._ResetEvent()
        self._ResetEvent()
        del self._gen
        super(CustomTipWindow, self).OnDestroy()

    # -----------------------------------------------------------------------------------

    def SetValue(self, mgs):
        # type: (str) -> None
        """设置文本"""
        self._context = mgs
        self.SetActive()

    def SetActive(self, isOn=True):
        if isOn and not self.IsActive():
            self._ActiveEvent()
        elif not isOn and self.IsActive():
            self._ResetEvent()
        super(CustomTipWindow, self).SetActive(isOn)
        if isOn:
            self._ResetContext()

    def SetFadeIn(self, value):
        # type: (int) -> None
        """设置渐变时间"""
        self._fade_in = max(0, value)

    def SetFadeOut(self, value):
        # type: (int) -> None
        """设置渐出时间"""
        self._fade_out = max(0, value)

    def SetDuration(self, value):
        # type: (int) -> None
        """设置常显时间"""
        self._duration = max(1, value)

    def SetMoveRange(self, min_range, max_range):
        # type: (float, float) -> None
        """配置相对父级面板移动百分比区间"""
        self._move_range = (min_range, max_range)

    def SetFixPos(self, pos):
        # type: (tuple) -> None
        """设置显示位置"""
        self._fix_pos = pos

    def ResetFixPos(self):
        """重置显示位置"""
        self._fix_pos = None

    def Display(self, visible):
        # type: (bool) -> None
        """显示"""
        self.SetVisible(self._parent, visible)

    # -----------------------------------------------------------------------------------

    def _ActiveEvent(self):
        """启动监听"""
        self.ListenDefaultEvent(ClientEvent.OnScriptTickClient, self._OnScriptTickClient, self)

    def _ResetEvent(self):
        """关闭监听"""
        self.UnListenDefaultEvent(ClientEvent.OnScriptTickClient, self._OnScriptTickClient, self)

    def _ResetContext(self):
        """重置文本显示"""
        self._tick = 0
        self._gen = self._CreateGen()

    def _CreateGen(self):
        image = self.GetImageUIControl(self._image)
        image.SetVisible(False)
        self.SetLabelText(self._label, self._context)
        image.SetAlpha(0)
        image.SetVisible(True)
        winSize = self.GetCompSize(self._parent)
        compSize = image.GetSize()
        centerPos = self.GetRelativeCenterPos(image)
        image.SetPosition((centerPos[0], winSize[1] * self._move_range[0]))
        """渐变全显"""
        if self._fade_in == 0:
            image.SetAlpha(1)
            if self._fix_pos:
                image.SetPosition(self._fix_pos)
            else:
                posY = winSize[1] * self._move_range[1] - compSize[1]
                image.SetPosition((centerPos[0], posY))
        else:
            for i in xrange(self._fade_in + 1):
                yield 1
                rate = float(i) / self._fade_in
                image.SetAlpha(rate)
                position = self._fix_pos
                if not position:
                    posY = winSize[1] * Misc.GetValueFromRate(rate, *self._move_range) - compSize[1]
                    position = (centerPos[0], posY)
                image.SetPosition(position)
        # -----------------------------------------------------------------------------------
        """全显时间"""
        yield self._duration
        # -----------------------------------------------------------------------------------
        """渐变全隐"""
        if self._fade_out == 0:
            image.SetAlpha(0)
        else:
            for i in xrange(self._fade_out + 1):
                yield 1
                rate = 1 - float(i) / self._fade_out
                image.SetAlpha(rate)
        # -----------------------------------------------------------------------------------
        image.SetVisible(False)
        self.SetLabelText(self._label, "")
        self.floatText = None

    def _OnScriptTickClient(self):
        """客户端Tick"""
        if self._gen:
            self._tick -= 1
            if self._tick > 0:
                return
            try:
                self._tick = self._gen.next()
            except StopIteration:
                self._gen = None
                self.SetActive(False)


# Version 1.1
class ImageDragMgr(object):
    """屏幕组件拖拽管理"""

    def __init__(self, ui_node, path, detect, **kwargs):
        self.ui_node = ui_node
        self.touchPos = (0, 0)
        self.detect = self.ui_node.GetBaseUIControl(detect).asButton()

        self._comp = self.ui_node.GetBaseUIControl(path)

        self.left = kwargs.get("left", -0.2)
        self.right = kwargs.get("right", 0.2)
        self.up = kwargs.get("up", -0.2)
        self.down = kwargs.get("down", 0.2)

    def Create(self):
        self.ui_node.SetButtonBind(self.detect, self._OnScreenTouchDown, method=TouchEvent.TouchDown)
        self.ui_node.SetButtonBind(self.detect, self._OnScreenCancelTouch, method=TouchEvent.TouchCancel)
        self.ui_node.SetButtonBind(self.detect, self._OnScreenDragging, method=TouchEvent.TouchMove)

    # -----------------------------------------------------------------------------------

    def _OnScreenTouchDown(self, _):
        self.touchPos = map(int, clientApi.GetTouchPos())

    def _OnScreenCancelTouch(self, _):
        self.touchPos = (0, 0)

    def _OnScreenDragging(self, _):
        touchPos = map(int, clientApi.GetTouchPos())

        offset = Misc.GetPosModify(touchPos, self.touchPos, method="sub")
        prePos, compSize = self.ui_node.GetCompInfo(self._comp)
        posX, posY = Misc.GetPosModify(prePos, offset)

        posX = Misc.GetClamp(posX, self.left * compSize[0], self.right * compSize[0])
        posY = Misc.GetClamp(posY, self.up * compSize[1], self.down * compSize[1])
        self._comp.SetPosition((posX, posY))
        self.touchPos = touchPos
