# -*- coding:utf-8 -*-


from ..module.preset import *

view_binder = clientApi.GetViewBinderCls()


class WidgetBase(UIModuleBase):
    """UI组件基类"""
    _widget_type = ""  # 组件类型
    _widget_mould = ""  # 组件模板路径

    def __init__(self, ui_node, root, *args, **kwargs):
        super(WidgetBase, self).__init__(ui_node)
        self.root = root
        self.visible = None

    def __del__(self):
        print "[warn]", "del: %s" % self.__class__.__name__

    def SetWidgetName(self, name):
        # type: (str) -> None
        """设置组件属性名"""
        path = self.root + "/image/label"
        self.SetLabelText(path, name)

    def SetWidgetVisible(self, visible):
        # type: (bool) -> None
        """设置可见"""
        if self.visible == visible:
            return
        self.visible = visible
        self.SetVisible(self.root, self.visible)

    def GetPosition(self):
        # type: () -> tuple
        """获得组件位置"""
        return self.GetCompPos(self.root)

    def GetSize(self):
        # type: () -> tuple
        """获得组件尺寸"""
        return self.GetCompSize(self.root)

    @classmethod
    def GetType(cls):
        # type: () -> str
        """获得组件类型"""
        return cls._widget_type

    @classmethod
    def GetMouldPath(cls):
        """获得模板路径"""
        return cls._widget_mould


class WidgetInput(WidgetBase):
    """输入组件"""
    _widget_type = "input"
    _widget_mould = "/panel_unit/panel_input"

    def __init__(self, ui_node, root, *args, **kwargs):
        super(WidgetInput, self).__init__(ui_node, root, *args, **kwargs)
        self.input_path = self.root + "/image/edit_box"
        self.input_comp = self.GetTextEditBoxUIControl(self.input_path)

    def GetInputText(self):
        return self.input_comp.GetEditText()


class WidgetToggle(WidgetBase):
    """反转组件"""
    _widget_type = "toggle"
    _widget_mould = "/panel_unit/panel_toggle"

    def __init__(self, ui_node, root, *args, **kwargs):
        super(WidgetToggle, self).__init__(ui_node, root, *args, **kwargs)
        self.toggle_path = self.root + "/image/switch_toggle"
        self.toggle_comp = self.GetSwitchToggleUIControl(self.toggle_path)
        self.toggle_state = True


    def SetToggleState(self, state):
        # type: (bool) -> None
        """设置翻转状态"""
        self.toggle_comp.SetToggleState(state)


class WidgetNum(WidgetBase):
    """数值组件"""
    _widget_type = "number"
    _widget_mould = "/panel_unit/panel_num"

    def __init__(self, ui_node, root, size, *args, **kwargs):
        super(WidgetNum, self).__init__(ui_node, root, *args, **kwargs)
        self.size = size


class WidgetSlider(WidgetBase):
    """滑动条组件"""
    _widget_type = "slider"
    _widget_mould = "/panel_unit/panel_slider"

    def __init__(self, ui_node, root, *args, **kwargs):
        super(WidgetSlider, self).__init__(ui_node, root, *args, **kwargs)
        self.slider_path = self.root + "/image/slider"
        self.slider_comp = self.GetSliderUIControl(self.slider_path)
        self.value_path = self.root + "/image/num"
        self.value_comp = WidgetNum(ui_node, self.value_path, 1)


class WidgetMgr(UIModuleBase):
    """组件管理"""
    __mVersion__ = 1

    def CreateInputWidget(self, parent, name):
        """创建输入组件"""
        root = self.CloneComp(WidgetInput.GetMouldPath(), parent, name)
        return WidgetInput(self.ui_node, root)

    def CreateToggleWidget(self, parent, name):
        """创建反转组件"""
        root = self.CloneComp(WidgetToggle.GetMouldPath(), parent, name)
        return WidgetToggle(self.ui_node, root)

    def CreateNumWidget(self, parent, name, size=1):
        """创建数值组件"""
        root = self.CloneComp(WidgetNum.GetMouldPath(), parent, name)
        return WidgetNum(self.ui_node, root, size)

    def CreateSliderWidget(self, parent, name):
        """创建滑动条组件"""
        root = self.CloneComp(WidgetSlider.GetMouldPath(), parent, name)
        return WidgetSlider(self.ui_node, root)
