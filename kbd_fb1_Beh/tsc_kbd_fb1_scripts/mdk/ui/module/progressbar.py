# -*- coding:utf-8 -*-


from base import UIModuleBase
from ..system.preset import *
from ...common.utils.misc import Algorithm


class CustomProgressBar(UIModuleBase):
    """自定义进度条"""
    __mVersion__ = 1

    def __init__(self, ui_node, target, **kwargs):
        super(CustomProgressBar, self).__init__(ui_node)
        self.empty_path = target
        self.full_path = kwargs.get("full_path", target + "/image_full")

        self.empty_image = self.GetImageUIControl(self.empty_path)
        self.full_image = self.GetImageUIControl(self.full_path)

    def SetClipDirection(self, mode=0):
        # type: (int) -> bool
        """
        设置图片控件的裁剪方向\n
        - mode=0: 从下到上
        - mode=1: 从左到右
        - mode=2: 从右到左
        - mode=3: 从外到内
        - mode=4: 从上到下
        """
        direction = self.GetClipDirection(mode)
        return self.full_image.SetClipDirection(direction)

    def SetValue(self, value):
        # type: (float) -> None
        """设置百分比值"""
        self.full_image.SetSpriteClipRatio(1 - value)


class HudProgressBarMgr(UIModuleBase):
    """进度条模块"""
    __mVersion__ = 9

    def __init__(self, ui_node, path, label=None, custom=False, **kwargs):
        super(HudProgressBarMgr, self).__init__(ui_node)
        self._tick = 0
        self._last_value = 0
        self._generator = None
        # -----------------------------------------------------------------------------------
        """进度条控件"""
        if custom:
            self.bar = CustomProgressBar(ui_node, path, **kwargs)
        else:
            self.bar = self.GetProgressBarUIControl(path)
        # -----------------------------------------------------------------------------------
        """文本控件"""
        self._text_format = lambda pre_value, max_value: "§l%d / %d" % (pre_value, max_value)
        self._label_comp = None
        self._show_label = False
        self._text_recall = None
        if label:
            path = self.GetCompPath(label)
            self._label_comp = self.GetLabelUIControl(path)
        # -----------------------------------------------------------------------------------
        self._rate_formula = lambda rate: rate
        if "modify_range" in kwargs:
            self.ConfigRateFormat(kwargs["modify_range"])
        # -----------------------------------------------------------------------------------
        self._get_max = lambda: 100
        if "pre" in kwargs:
            self.ConfigGetPre(kwargs["pre"])
        # -----------------------------------------------------------------------------------
        self._get_pre = lambda: 0
        if "max" in kwargs:
            self.ConfigGetMax(kwargs["max"])

    def OnDestroy(self):
        MDKConfig.GetModuleClient().StopCoroutine(self._generator)
        del self._generator
        del self._text_format
        del self._rate_formula
        del self._text_recall
        del self._get_max
        del self._get_pre
        super(HudProgressBarMgr, self).OnDestroy()

    def ConfigEvent(self):
        super(HudProgressBarMgr, self).ConfigEvent()
        self.defaultEvent[ClientEvent.OnScriptTickClient] = self._OnScriptTickClient

    # -----------------------------------------------------------------------------------

    def ConfigGetPre(self, func):
        """
        配置获得目前值的函数\n
        在初始化模块时需要配置\n
        - 可使用预设生命值
        - 一般使用服务端传来的数据
        - 例如显示法力：lambda: self.GetPlayerData("mana")
        """
        if not callable(func):
            print "[error]", "该函数不可调用：%s" % func
            return
        self._get_pre = func
        return self

    def ConfigGetMax(self, func):
        """
        配置获得最大值的函数\n
        在初始化模块时需要配置\n
        - 可使用预设生命值
        - 一般使用服务端传来的数据
        - 例如显示最大法力：lambda: self.GetPlayerData("max_mana")
        """
        if not callable(func):
            print "[error]", "该函数不可调用：%s" % func
            return
        self._get_max = func
        return self

    def ConfigRateFormat(self, formula):
        """
        配置进度条比例\n
        用于一些不完整进度条的情况修正\n
        - 默认：lambda rate: rate
        - 举例：lambda rate: rate * 0.75 + 0.25
        """
        if not callable(formula):
            print "[error]", "进度条比例公式不可调用"
            return
        self._rate_formula = formula
        return self

    def ConfigTextFormat(self, rules):
        """
        配置文字显示的格式\n
        - 默认 -> lambda pre_value, max_value: "§l%d / %d" % (pre_value, max_value)
        """
        self._text_format = rules

    def ConfigTextRecall(self, recall):
        # type: (any) -> HudProgressBarMgr
        """
        配置设置文本回调\n
        - pre_value: float
        - max_value: float
        """
        self._text_recall = recall
        return self

    def SetActive(self, isOn):
        super(HudProgressBarMgr, self).SetActive(isOn)
        if not isOn:
            self._generator = None

    def ResetConfig(self):
        """重置当前值和最大值获取"""
        self._get_pre = None
        self._get_max = None

    # -----------------------------------------------------------------------------------

    def SetValue(self, rate):
        # type: (float) -> None
        """
        设置进度条百分比\n
        - 一般用于新数据到界面强更数据显示
        """
        value = self._rate_formula(rate)
        self.bar.SetValue(value)
        self._last_value = self._GetMaxValue() * rate

    def SetText(self, rate):
        # type: (float) -> None
        """
        设置进度条文字\n
        - 一般用于新数据到界面强更数据显示
        """
        maxValue = self._GetMaxValue()
        preValue = math.ceil(rate * maxValue)
        if self._text_recall:
            self._text_recall(preValue, maxValue)
        if self._label_comp:
            self._label_comp.SetText(self._text_format(preValue, maxValue))

    # -----------------------------------------------------------------------------------

    def _OnScriptTickClient(self):
        if not self._active:
            return

        self._tick += 1
        if self._tick >= 3:
            self._tick = 0
            # 检测是否更新
            self._CheckBarState()
        # -----------------------------------------------------------------------------------
        if self._generator:
            # 更新进度条信息
            self._UpdateBarProgress()

    def _CheckBarState(self):
        """检测进度条状态"""
        preValue = self._GetPreValue()
        if self._label_comp and not self._show_label:
            self._show_label = True
        else:
            if self._last_value == preValue:
                return
        maxValue = float(self._GetMaxValue())
        preRate = self._last_value / maxValue
        newRate = preValue / maxValue
        # 获取序列生成器
        self._generator = Algorithm.lerp(preRate, newRate, 0.2, 0.01)
        # 修正上次数值
        self._last_value = preValue

    def _UpdateBarProgress(self):
        """更新进度条状态"""
        try:
            preRate = self._generator.next()
        except StopIteration:
            self._generator = None
            return
        self.SetValue(preRate)
        self.SetText(preRate)

    def _GetMaxValue(self):
        """获得进度条最大值"""
        if not callable(self._get_max):
            return 1
        maxValue = self._get_max()
        if not maxValue:
            return 1
        return max(1, maxValue)

    def _GetPreValue(self):
        """获得精度条目前值"""
        if not callable(self._get_pre):
            return 0
        preValue = self._get_pre()
        if not preValue:
            return 0
        return preValue

    # -----------------------------------------------------------------------------------

    def PresetHealth(self):
        """用于生命的预设"""
        self._get_pre = lambda: self.local_player.health
        self._get_max = lambda: self.local_player.max_health
        return self


class RollProgressMgr(UIModuleBase):
    """进度条动画管理"""
    __mVersion__ = 3

    def __init__(self, ui_node, path, **kwargs):
        super(RollProgressMgr, self).__init__(ui_node, manual_listen=True)
        self._on_tick = False
        self._path = path
        self._comp = self.GetProgressBarUIControl(self._path)

        self._pre = 0
        self._gen = None
        self._set_recall = None

        self._formula = kwargs.get("formula", lambda start, end: Algorithm.parabola_blend_float(start, end, 25))
        self._map = kwargs.get("map")
        self._mapRange = kwargs.get("map_range", lambda x: Algorithm.map_range(x, 0, 1, 0, 1))
        if self._map:
            self._ActiveEvent()

    def OnDestroy(self):
        if self._on_tick:
            self._ResetEvent()
        del self._comp
        del self._formula
        del self._map
        del self._mapRange
        super(RollProgressMgr, self).OnDestroy()

    # -----------------------------------------------------------------------------------

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

    def ConfigSetRecall(self, recall):
        """
        配置设置值时回调\n
        - 默认传入 float->pre_value 当前百分比作为参数
        """
        if not callable(recall):
            print "[error]", "无效回调函数"
            return
        self._set_recall = recall

    def ConfigMapRange(self, rule):
        """
        配置百分比压缩比\n
        - 将压缩至至目标区间
        - 默认 lambda x: Algorithm.map_range(x, 0, 1, 0, 1)
        """
        self._mapRange = rule

    # -----------------------------------------------------------------------------------

    def SetValue(self, value):
        # type: (float) -> None
        """设置进度条百分比"""
        if value == self._pre:
            return
        self._gen = self._formula(self._pre, value)
        if not self._on_tick:
            self._ActiveEvent()

    def SetValueWithoutAnim(self, value):
        # type: (float) -> None
        """
        设置进度条百分比\n
        - 不含有动画
        """
        self._pre = value
        self._gen = None
        self._comp.SetValue(value)

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
            if self._mapRange:
                self._pre = self._mapRange(self._pre)
            self._OnSetValue(self._pre)

    def _OnSetValue(self, value):
        # type: (float) -> None
        """控件设置百分比值"""
        self._comp.SetValue(value)
        # 设置值回调
        if self._set_recall:
            self._set_recall(value)

    def _ActiveEvent(self):
        self._on_tick = True
        self.ListenDefaultEvent(ClientEvent.OnScriptTickClient, self._OnScriptTickClient)

    def _ResetEvent(self):
        self._on_tick = False
        self.UnListenDefaultEvent(ClientEvent.OnScriptTickClient, self._OnScriptTickClient)
