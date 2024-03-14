# -*- coding:utf-8 -*-


from base import UIModuleBase
from ..system.preset import *
from ...common.utils.misc import Algorithm


class VerbatimLabel(UIModuleBase):
    """逐字显示文本"""
    __mVersion__ = 2

    def __init__(self, ui_node, path, **kwargs):
        super(VerbatimLabel, self).__init__(ui_node, **kwargs)
        self._on_tick = False
        self._path = path
        self._comp = self.GetLabelUIControl(self._path)

        self._speed_mode = True  # 默认固定速度显示模式
        self._speed = kwargs.get("speed", 1)
        self._speed_index = 0
        self._text_len = 0
        self._duration = 0
        self._suffix = kwargs.get("suffix", "")
        self._max_duration = kwargs.get("duration", 0)
        if self._max_duration > 0:
            self.ConfigDisplayDuration(self._max_duration)

        self._recall = None
        recall = kwargs.get("recall")
        if recall:
            self.ConfigRecall(recall)

        self._text = kwargs.get("text", "")
        if self._text:
            self.SetText(self._text)

    def OnDestroy(self):
        if self._on_tick:
            self._ResetEvent()
        del self._comp
        del self._recall
        super(VerbatimLabel, self).OnDestroy()

    # -----------------------------------------------------------------------------------

    def ConfigDisplayDuration(self, duration):
        # type: (float) -> None
        """
        配置显示完整个文本的固定时间\n
        - 配置后将屏蔽固定速度显示机制
        - 默认固定时间： 1.0s -> 30tick
        """
        self._max_duration = max(1, int(30 * duration))
        self._speed_mode = False

    def ConfigDisplaySpeed(self, speed):
        # type: (int) -> None
        """
        配置显示速度\n
        - 配置后将屏蔽固定时间显示机制
        """
        self._speed = speed
        self._speed_mode = True

    def ConfigRecall(self, recall):
        """配置显示回调"""
        if not callable(recall):
            print "[error]", "无效回调函数", recall
            return
        self._recall = recall

    def ConfigDisplaySuffix(self, text):
        # type: (str) -> None
        """配置显示文本时的后缀"""
        self._suffix = text

    # -----------------------------------------------------------------------------------

    def SetText(self, text):
        # type: (str) -> None
        """设置显示文本"""
        self._text = text
        # 重置显示变量
        self._duration = self._max_duration
        self._text_len = len(self._text)
        self._speed_index = 0

        if not self._on_tick:
            self._ActiveEvent()

    def SetDisplayRate(self, rate):
        # type: (float) -> None
        """设置显示的进度"""
        if not self._on_tick:
            return
        if self._speed_mode:
            self._speed_index = int(math.ceil(rate * self._text_len))
        else:
            self._duration = rate * self._max_duration

    def GetText(self):
        # type: () -> str
        """获得本次显示的文本"""
        return self._text

    # -----------------------------------------------------------------------------------

    def _OnScriptTickClient(self):
        """客户端Tick"""
        self._DisplayOnSpeedMode() if self._speed_mode else self._DisplayOnDurationMode()

    def _DisplayOnDurationMode(self):
        """固定时长模式显示"""
        self._duration -= 1
        rate = 1 - self._duration / float(self._max_duration)
        # -----------------------------------------------------------------------------------
        index = int(math.ceil(rate * self._text_len))
        text = self._text[:index]
        # -----------------------------------------------------------------------------------
        """后缀显示"""
        if self._duration > 0 and self._suffix:
            text += self._suffix
        # -----------------------------------------------------------------------------------
        self._comp.SetText(text)
        # -----------------------------------------------------------------------------------
        """显示完关闭"""
        if self._duration <= 0:
            self._OnFinishedDisplay()

    def _DisplayOnSpeedMode(self):
        """固定速度模式显示"""
        self._speed_index += self._speed
        text = self._text[:self._speed_index]
        # -----------------------------------------------------------------------------------
        """后缀显示"""
        if self._speed_index < self._text_len and self._suffix:
            text += self._suffix
        # -----------------------------------------------------------------------------------
        self._comp.SetText(text)
        # -----------------------------------------------------------------------------------
        """显示完关闭"""
        if self._speed_index >= self._text_len:
            self._OnFinishedDisplay()

    def _OnFinishedDisplay(self):
        """显示完成回调"""
        self.SetActive(False)
        if self._recall:
            recall = self._recall
            self._recall = None
            recall()
        self._ResetEvent()

    def _ActiveEvent(self):
        self._on_tick = True
        self.ListenDefaultEvent(ClientEvent.OnScriptTickClient, self._OnScriptTickClient)

    def _ResetEvent(self):
        self._on_tick = False
        self.UnListenDefaultEvent(ClientEvent.OnScriptTickClient, self._OnScriptTickClient)


class RollNumberMgr(UIModuleBase):
    """数字动画管理"""
    __mVersion__ = 3

    def __init__(self, ui_node, path, **kwargs):
        super(RollNumberMgr, self).__init__(ui_node, manual_listen=True)
        self._on_tick = False
        self._path = path
        self._comp = self.GetLabelUIControl(self._path)

        self._pre = 0
        self._gen = None

        self._text_format = kwargs.get("format", lambda value: "§l%d" % value)
        self._formula = kwargs.get("formula", lambda start, end: Algorithm.parabola_blend_int(start, end, 25))
        self._map = kwargs.get("map")
        if self._map:
            self._ActiveEvent()

    def OnDestroy(self):
        if self._on_tick:
            self._ResetEvent()
        del self._comp
        del self._text_format
        del self._formula
        del self._map
        super(RollNumberMgr, self).OnDestroy()

    # -----------------------------------------------------------------------------------

    def ConfigFormat(self, rule):
        """
        配置输出格式\n
        - 默认：lambda value: "§l%d" % value
        """
        self._text_format = rule

    def ConfigFormula(self, rule):
        """配置数学公式"""
        self._formula = rule

    def ConfigMap(self, rule):
        """配置值映射"""
        if not callable(rule):
            print "[error]", "值映射函数不可调用"
            return
        self._map = rule
        if not self._on_tick:
            self._ActiveEvent()

    # -----------------------------------------------------------------------------------

    def SetValue(self, value):
        # type: (int) -> None
        """设置文本值"""
        if value == self._pre:
            return
        self._gen = self._formula(self._pre, value)
        if not self._on_tick:
            self._ActiveEvent()

    def SetValueWithoutAnim(self, value):
        # type: (int) -> None
        """
        设置文本值\n
        - 不含有动画
        """
        self._pre = value
        self._gen = None
        self._OnSetCompValue(self._pre)

    # -----------------------------------------------------------------------------------

    def _OnScriptTickClient(self):
        """客户端Tick"""
        if not self.IsActive():
            return
        # -----------------------------------------------------------------------------------
        if self._map and not self._gen:
            new_value = self._map()
            if new_value != self._pre:
                self.SetValue(new_value)
        if self._gen:
            try:
                self._pre = self._gen.next()
            except StopIteration:
                self._gen = None
                if not self._map:
                    self._ResetEvent()
                return
            self._OnSetCompValue(self._pre)

    def _OnSetCompValue(self, value):
        # type: (int) -> None
        """设置控件文本值"""
        text = self._text_format(value)
        self._comp.SetText(str(text))

    def _ActiveEvent(self):
        self._on_tick = True
        self.ListenDefaultEvent(ClientEvent.OnScriptTickClient, self._OnScriptTickClient)

    def _ResetEvent(self):
        self._on_tick = False
        self.UnListenDefaultEvent(ClientEvent.OnScriptTickClient, self._OnScriptTickClient)
