# -*- coding:utf-8 -*-


from functools import wraps

from mod.common.minecraftEnum import KeyBoardType

from preset import *
from ....common.utils.misc import Misc
from ....ui.module import *
from ....ui.widget.base import WidgetMgr

if __name__ == '__main__':
    from ..server import DebugModuleServer
    from ..client import DebugModuleClient


def hide_menu(func):
    """隐藏下拉菜单"""

    @wraps(func)
    def warped(*args, **kwargs):
        res = func(*args, **kwargs)
        ui_node = args[0]  # type: OptionScreen
        ui_node.HideAllMenuOption()
        return res

    return warped


class DebugScreen(UIModuleManagerPreset):
    """debug模块UI"""
    __mVersion__ = 9

    def __init__(self, namespace, name, param):
        super(DebugScreen, self).__init__(namespace, name, param)

        self.pop_screen = PopScreen(self)
        self.function_screen = FunctionScreen(self)
        self.option_screen = OptionScreen(self)
        self.widget_mgr = WidgetMgr(self)
        self.rpc_ui = None

        # 拖拽界面
        self.state_drag_win = False
        self.drag_cache = {}
        self.win_comp = None

    def OnDestroy(self):
        self.widget_mgr.OnDestroy()
        del self.widget_mgr
        del self.win_comp
        self.pop_screen.OnDestroy()
        self.function_screen.OnDestroy()
        self.option_screen.OnDestroy()
        del self.pop_screen
        del self.function_screen
        del self.option_screen
        self.rpc_ui.Discard()
        del self.rpc_ui
        self.UnRegisterKeyPressRecall(KeyBoardType.KEY_Q, self.OnKeyPressCheck)
        super(DebugScreen, self).OnDestroy()

    def ConfigEvent(self):
        super(DebugScreen, self).ConfigEvent()
        self.defaultEvent.update({
            ClientEvent.ClientJumpButtonReleaseEvent: self.ClientJumpButtonReleaseEvent,
            ClientEvent.TapBeforeClientEvent: self.TapBeforeClientEvent,
        })

    def Create(self):
        super(DebugScreen, self).Create()
        self.SetVisible("/panel_debug", True)
        self.SetVisible("/panel_skill", True)
        self.rpc_ui = self.ModuleSystem.CreateRpcModule(self, "debug.ui")

        # 拖拽绑定
        self.win_comp = self.GetBaseUIControl("/panel_debug/panel_win")
        path = "/panel_debug/panel_win/drag"
        self.SetButtonBind(path, self.KeyRecallDragWinTouch, TouchEvent.TouchDown)
        self.SetButtonBind(path, self.KeyRecallDragWinActive, TouchEvent.TouchMove)
        self.SetButtonBind(path, self.KeyRecallDragWinCancel, TouchEvent.TouchUp)
        self.SetButtonBind(path, self.KeyRecallDragWinCancel, TouchEvent.TouchCancel)

        # 界面创建绑定
        self.pop_screen.Create()
        self.function_screen.Create()
        self.option_screen.Create()

        # 客户端绑定界面
        module = self.ModuleSystem.GetModule("debug")  # type: DebugModuleClient
        module.debug_ui = weakref.proxy(self)

        self.RegisterKeyPressRecall(KeyBoardType.KEY_Q, self.OnKeyPressCheck)

    def Update(self):
        self.option_screen.Update()

    # -----------------------------------------------------------------------------------

    @property
    def server(self):
        # type: () -> DebugModuleServer
        return self.rpc_ui

    # -----------------------------------------------------------------------------------

    def KeyRecallDragWinTouch(self, _):
        """窗口拖动按下"""
        self.option_screen.HideAllMenuOption()

    def KeyRecallDragWinActive(self, args):
        if self.option_screen.is_full_win:
            # 全屏窗口无法拖动
            return

        path = args["ButtonPath"]  # type: str
        touch_pos = (args["TouchPosX"], args["TouchPosY"])
        if path not in self.drag_cache:
            comp_pos = self.GetCompPos("/panel_debug/panel_win")
            self.drag_cache[path] = Misc.GetPosModify(touch_pos, comp_pos, method="sub")
        self.win_comp.SetPosition(Misc.GetPosModify(touch_pos, self.drag_cache[path], method="sub"))

    def KeyRecallDragWinCancel(self, args):
        path = args["ButtonPath"]  # type: str
        self.drag_cache.pop(path, None)

    # -----------------------------------------------------------------------------------

    def OnResponseStorageKeyCheck(self, key, available):
        """响应数据键检测"""
        return self.option_screen.OnResponseCheckStorageKey(key, available)

    def OnUpdateScrollText(self, key, data):
        # type: (str, dict) -> None
        """更新滚动列表文本"""
        context = ["server storage key： <%s>\n" % key]

        def parse_list(_data, indent, _title=None):
            """解析列表"""
            if _title:
                context.append(" " * (indent - 2) + "%s: <list>" % _title)
                context.append(" " * (indent - 2) + "[")
            for _value in _data:
                if isinstance(_value, dict):
                    parse_dict(_value, indent + 2)
                elif isinstance(_value, list):
                    parse_list(_value, indent + 2)
                else:
                    if _value == "":
                        _value = "\"\""
                    context.append(" " * indent + _value)
            context.append(" " * (indent - 2) + "]")

        def parse_dict(_data, indent, _title=None):
            if _title:
                context.append(" " * (indent - 2) + "%s: <dict>" % _title)
                context.append(" " * (indent - 2) + "{")
            for _key, _value in _data.items():
                if isinstance(_value, dict):
                    parse_dict(_value, indent + 2, _key)
                    continue
                elif isinstance(_value, list):
                    parse_list(_value, indent + 2, _key)
                else:
                    if _value == "":
                        _value = "\"\""
                    context.append(" " * indent + "%s: %s" % (_key, _value))
            context.append(" " * (indent - 2) + "}")

        parse_dict(data, 2, key)
        text = "\n".join(context).replace("%", "%%")
        self.option_screen.SetScrollText(text)

    def OnResponseModuleInfo(self, data):
        # type: (dict) -> None
        """响应模块信息"""
        self.option_screen.preset_query.OnResponseModuleInfo(data)

    def SetInputPanelTips(self, context):
        # type: (str) -> None
        """设置输入面板的提示信息"""
        self.pop_screen.SetInputPanelTips(context)

    # -----------------------------------------------------------------------------------

    def OnKeyPressCheck(self):
        """按键按下检测"""
        if self.GetKeyState(KeyBoardType.KEY_R):
            self.option_screen.ToggleMainScreenVisible()

    def ClientJumpButtonReleaseEvent(self, args):
        pass
        # self.option_screen.ToggleMainScreenVisible()

    def TapBeforeClientEvent(self, args):
        # 隐藏所有下拉菜单
        self.option_screen.HideAllMenuOption()


class PopScreen(UIModuleSubPagePreset):
    """弹出界面"""
    __mVersion__ = 2

    def __init__(self, mgr, **kwargs):
        super(PopScreen, self).__init__(mgr, **kwargs)
        self.mgr = weakref.proxy(mgr)  # type: DebugScreen
        # 输入确认回调
        self.input_recall = None
        # 输入界面显示
        self.visible_input_screen = True
        # 弹窗界面显示
        self.visible_pop_screen = True

    def Create(self):
        self.SetButtonBind("/panel_debug/panel_pop/input/confirm", self.KeyRecallConfirmInput)
        self.SetButtonBind("/panel_debug/panel_pop/input/cancel", self.KeyRecallCancelInput)

        # 关闭界面
        self.SetInputPanelVisible(False)
        self.SetPopScreenVisible(False)

    # -----------------------------------------------------------------------------------

    def KeyRecallConfirmInput(self, _):
        """输入面板确认按钮"""
        if not callable(self.input_recall):
            self.input_recall = None
            return
        self.input_recall(self.GetInputContext())
        self.input_recall = None
        self.SetInputPanelVisible(False)

    def KeyRecallCancelInput(self, _):
        """输入面板取消按钮"""
        self.input_recall = None
        self.SetInputPanelVisible(False)

    # -----------------------------------------------------------------------------------

    """输入面板"""

    def GetInputContext(self):
        # type: () -> str
        """获得输入内容"""
        path = "/panel_debug/panel_pop/input/edit_box"
        context = self.GetTextEditBoxUIControl(path).GetEditText()
        if not context:
            return ""
        return context

    def SetInputPanelVisible(self, visible):
        """设置输入面板显示"""
        if visible == self.visible_input_screen:
            return
        self.visible_input_screen = visible
        self.SetVisible("/panel_debug/panel_pop/input", visible)
        self.comp_factory.CreateOperation(self.local_id).SetCanAll(False)
        if not visible:
            self.SetPopScreenVisible(False)
            self.comp_factory.CreateOperation(self.local_id).SetCanAll(not self.mgr.option_screen.focus_mode)

    def SetInputPanelConfig(self, title, recall, tip=""):
        # type: (str, any, str) -> None
        """设置输入面板配置"""
        self.SetLabelText("/panel_debug/panel_pop/input/label", title)
        self.input_recall = recall
        self.SetPopScreenVisible(True)
        self.SetInputPanelVisible(True)
        self.SetInputPanelTips(tip)

    def SetInputPanelTips(self, tip):
        # type: (str) -> None
        """设置输入面板的提示内容"""
        self.SetLabelText("/panel_debug/panel_pop/input/tips/label", tip)

    def SetPopScreenVisible(self, visible):
        """设置弹窗界面显示"""
        if visible == self.visible_pop_screen:
            return
        self.visible_pop_screen = visible
        self.SetVisible("/panel_debug/panel_pop", self.visible_pop_screen)


class FunctionScreen(UIModuleSubPagePreset):
    """功能界面"""
    __mVersion__ = 3

    def __init__(self, mgr, **kwargs):
        super(FunctionScreen, self).__init__(mgr, **kwargs)
        self.mgr = weakref.proxy(mgr)  # type: DebugScreen
        self.alpha_slider = None
        self.time_slider = None
        # 滚动列表设置
        self.scroll_setting_path = ""

    def OnDestroy(self):
        self.alpha_slider.OnDestroy()
        del self.alpha_slider
        self.time_slider.OnDestroy()
        del self.time_slider
        super(FunctionScreen, self).OnDestroy()

    def Create(self):
        # 滚动设置路径
        path = "/panel_debug/panel_win/context/panel_setting/scroll_view"
        self.scroll_setting_path = self.GetScrollContext(path)

        mould = self.scroll_setting_path + "/mould"
        # alpha setting
        root = self.CloneComp(mould, self.scroll_setting_path, "alpha")
        button = root + "/function/slider/button"
        label = root + "/name/label"
        self.alpha_slider = SliderMgr(self.mgr, button)
        self.alpha_slider.ConfigDragActiveRecall(self.OnAlphaSliderDragActiveRecall)
        # self.alpha_slider.ConfigDragCancelRecall(self.OnAlphaSliderDragCancelRecall)
        self.alpha_slider.dataTemp = label
        self.SetLabelText(label, "Alpha: 0%%")
        self.SetVisible(root, True)

        # time setting
        root = self.CloneComp(mould, self.scroll_setting_path, "time")
        button = root + "/function/slider/button"
        label = root + "/name/label"
        self.time_slider = SliderMgr(self.mgr, button)
        self.time_slider.ConfigDragActiveRecall(self.OnTimeSliderDragActiveRecall)
        # self.time_slider.ConfigDragCancelRecall(self.OnTimeSliderDragCancelRecall)
        self.time_slider.dataTemp = label
        self.SetLabelText(label, "Time: 0%%")
        self.SetVisible(root, True)

    # -----------------------------------------------------------------------------------

    """滑动条"""

    def OnAlphaSliderDragActiveRecall(self, slider):
        # type: (SliderMgr) -> None
        """滑动条拖动回调"""
        rate = slider.GetRate()
        self.SetOpacity("/panel_debug/panel_win/context", rate)
        self.SetLabelText(slider.dataTemp, "Alpha: %d%%%%" % (rate * 100))

    def OnAlphaSliderDragCancelRecall(self, slider):
        """save config"""

    def OnTimeSliderDragActiveRecall(self, slider):
        # type: (SliderMgr) -> None
        """滑动条拖动回调"""
        rate = slider.GetRate()
        self.mgr.server.SetWorldTime(rate)
        self.SetLabelText(slider.dataTemp, "Time: %d%%%%" % (rate * 100))

    def OnTimeSliderDragCancelRecall(self, slider):
        """滑动条拖动回调"""


class OptionScreen(UIModuleSubPagePreset):
    """按钮界面"""
    __mVersion__ = 7

    def __init__(self, mgr, **kwargs):
        super(OptionScreen, self).__init__(mgr, **kwargs)
        self.mgr = weakref.proxy(mgr)  # type: DebugScreen

        self.is_full_win = False  # 是否全屏

        # 专注模式：开启后无法移动和转视角
        self.focus_mode = False

        self.function_menu = None
        self.storage_menu = None
        self.module_menu = None
        self.query_menu = None

        self.preset_function = PresetFunction(self)
        self.preset_data = PresetData(self)
        self.preset_module = PresetModule(self)
        self.preset_query = PresetQuery(self)

        # 内容界面显示
        self.visible_context_screen = True
        # 设置界面显示
        self.visible_setting_screen = True
        # 制作界面显示
        self.visible_maker_screen = True
        # 滚动文本界面显示
        self.visible_scroll_screen = True
        # 主界面显示
        self.visible_main_screen = True

        self.win_selector = None  # 选择器
        self.selected_id = None

        self._data_path_map = {}  # 数据键路径对应

        # 滚动列表文本
        self.scroll_text_path = ""

        self.input_button_recall = None  # 输入确认按钮回调
        self.timer = None  # 循环更新数据界面定时器

    def OnDestroy(self):
        del self.win_selector
        del self.input_button_recall
        self.game_comp.CancelTimer(self.timer)
        del self.timer

        self.preset_function.OnDestroy()
        self.preset_data.OnDestroy()
        self.preset_module.OnDestroy()
        self.preset_query.OnDestroy()
        del self.preset_function
        del self.preset_data
        del self.preset_module
        del self.preset_query

        self.function_menu.OnDestroy()
        self.storage_menu.OnDestroy()
        self.module_menu.OnDestroy()
        self.query_menu.OnDestroy()
        del self.function_menu
        del self.storage_menu
        del self.module_menu
        del self.query_menu

        super(OptionScreen, self).OnDestroy()

    def Create(self):
        self.SetButtonBind("/panel_debug/panel_win/title/stack_options/button_hide", self.KeyRecallServerHide)
        self.SetButtonBind("/panel_debug/panel_win/title/stack_options/button_win", self.KeyRecallWinScale)
        self.SetButtonBind("/panel_debug/panel_win/title/stack_options/button_exit", self.KeyRecallExitScreen)
        self.SetButtonBind("/panel_debug/panel_win/title/stack_options/button_setting", self.KeyRecallSettingOption)
        path = "/panel_debug/panel_win/title/stack_options/button_selector"
        self.SetButtonBind(path, self.KeyRecallWinSelectorActive, TouchEvent.TouchDown)
        self.SetButtonBind(path, self.KeyRecallWinSelectorCancel, TouchEvent.TouchUp)
        self.SetButtonBind(path, self.KeyRecallWinSelectorCancel, TouchEvent.TouchCancel)
        self.SetButtonBind("/panel_debug/panel_win/title/stack_options/button_collision", self.KeyRecallToggleFocus)

        """功能菜单"""
        self.function_menu = MenuOptionComponent(self.mgr, "/panel_debug/panel_win/stack_menu/function/button")
        self.function_menu.SetMenuTitle("function")
        self.function_menu.SetSwitchVisible(False)
        self.function_menu.RegisterWillOpenMenuCallBack(self.HideAllMenuOption)
        self.function_menu.AddOption("pc-mode", callback=self.preset_function.TogglePcMode)
        # self.function_menu.AddOption("+Add New Button", callback=self.KeyRecallAddMenuOption)

        """数据菜单"""
        self.storage_menu = MenuOptionComponent(self.mgr, "/panel_debug/panel_win/stack_menu/storage/button")
        self.storage_menu.SetMenuTitle("data")
        self.storage_menu.SetSwitchVisible(False)
        self.storage_menu.RegisterWillOpenMenuCallBack(self.HideAllMenuOption)
        self.storage_menu.AddOption("+Add New Storage", callback=self.KeyRecallAddStorageMenu)

        """模块菜单"""
        self.module_menu = MenuOptionComponent(self.mgr, "/panel_debug/panel_win/stack_menu/module/button")
        self.module_menu.SetMenuTitle("module")
        self.module_menu.SetSwitchVisible(False)
        self.module_menu.RegisterWillOpenMenuCallBack(self.HideAllMenuOption)
        # 模块预设功能
        self.module_menu.AddOption("skill", callback=self.preset_module.SkillMakerScreen)
        self.module_menu.AddOption("render", callback=self.preset_module.RenderMakerScreen)

        """查询菜单"""
        self.query_menu = MenuOptionComponent(self.mgr, "/panel_debug/panel_win/stack_menu/query/button")
        self.query_menu.SetMenuTitle("query")
        self.query_menu.SetSwitchVisible(False)
        self.query_menu.RegisterWillOpenMenuCallBack(self.HideAllMenuOption)
        # 查询预设功能
        self.query_menu.AddOption("module", callback=self.preset_query.QueryModule)
        self.query_menu.AddOption("molang", callback=self.preset_query.QueryMolang)
        self.query_menu.AddOption("attribute", callback=self.preset_query.QueryAttribute)
        self.query_menu.AddOption("loot", callback=self.preset_query.QueryLoot)
        self.query_menu.AddOption("quest", callback=self.preset_query.QueryQuest)
        self.query_menu.AddOption("recipe", callback=self.preset_query.QueryRecipe)

        # 滚动列表文本路径
        path = "/panel_debug/panel_win/context/panel_scroll/scroll_view"
        self.scroll_text_path = self.GetScrollContext(path) + "/label"

        # 默认全屏
        self.KeyRecallWinScale({"force": True})

        # 关闭界面
        self.SetScrollScreenVisible(False)
        self.SetSettingScreenVisible(False)
        self.SetMainScreenVisible(False)

    def Update(self):
        if self.win_selector:
            size = self.GetCompCenterPos(self.win_selector)
            self.win_selector.SetPosition(Misc.GetPosModify(clientApi.GetTouchPos(), size, method="sub"))

    # -----------------------------------------------------------------------------------

    @hide_menu
    def KeyRecallWinScale(self, args):
        # type: (dict) -> None
        """窗口缩放回调"""
        width, height = self.game_comp.GetScreenSize()

        # 主界面尺寸
        main_path = "/panel_debug/panel_win"
        # 内容界面尺寸
        context_path = "/panel_debug/panel_win/context"

        if args.get("force") or not self.is_full_win:
            self.is_full_win = True
            self.SetCompSize(main_path, (1.0,), follow=("px",))
            self.SetCompPos(main_path, (0, 0))
            self.SetCompSize(context_path, (width, height - 20), resize_children=True)
        else:
            self.is_full_win = False
            width /= 2
            self.SetCompSize(main_path, (0.5,), follow=("px",))
            self.SetCompPos(main_path, (8, 8))
            self.SetCompSize(context_path, (width, 150), resize_children=True)

    @hide_menu
    def KeyRecallExitScreen(self, _):
        """退出按钮回调"""
        self.SetMainScreenVisible(False)

    @hide_menu
    def KeyRecallServerHide(self, _):
        # type: (dict) -> None
        """服务端窗口隐藏"""
        self.SetContextScreenVisible(not self.visible_context_screen)

    @hide_menu
    def KeyRecallSettingOption(self, _):
        """设置按钮回调"""
        self.SetSettingScreenVisible(not self.visible_setting_screen)

    @hide_menu
    def KeyRecallWinSelectorActive(self, _):
        """窗口选择器回调"""

        def active():
            image = "/panel_debug/panel_win/title/stack_options/button_selector/image_icon"
            self.SetVisible(image, False)
            yield 0
            root = self.CloneComp(image, "/panel_debug", "selector")
            self.win_selector = self.GetImageUIControl(root)
            self.SetCompSize(self.win_selector, (0.05,), follow=("px",))
            self.SetVisible(root, True)
            self.SetVisible(image, True)

        self.StartCoroutine(active)

    @hide_menu
    def KeyRecallWinSelectorCancel(self, _):
        """窗口选择器取消回调"""
        self.DelComp(self.win_selector)
        self.win_selector = None
        entity_id = self.camera_comp.GetChosenEntity()
        if entity_id:
            self.selected_id = entity_id
            print "[suc]", "选中实体：%s <%s>" % (self.selected_id, RawEntity.GetTypeStr(self.selected_id))

    @hide_menu
    def KeyRecallToggleFocus(self, _):
        self.comp_factory.CreateOperation(self.local_id).SetCanAll(self.focus_mode)
        self.focus_mode = not self.focus_mode

    # -----------------------------------------------------------------------------------

    @hide_menu
    def KeyRecallAddStorageMenu(self, _):
        """添加数据选项回调"""
        self.mgr.pop_screen.SetInputPanelConfig("Storage Key", self.OnConfirmInputStorageKey)
        # 数据键提示
        target_id = self.mgr.option_screen.selected_id
        if not target_id or not self.game_comp.IsEntityAlive(target_id):
            target_id = self.local_id
        self.mgr.server.RequestTargetStorageKey(self.local_id, target_id)

    @hide_menu
    def KeyRecallAddMenuOption(self, path):
        """添加菜单选项回调"""
        button_num = self.function_menu.GetOptionCount()
        self.function_menu.AddOption("Button%s" % (button_num + 1), callback=self.KeyRecallDelMenuOption)

    @hide_menu
    def KeyRecallDelMenuOption(self, path):
        """删除菜单选项回调"""
        self.function_menu.DelOptionByPath(path)

    @hide_menu
    def KeyRecallDisplayStorageData(self, args):
        # type: (dict) -> None
        """
        显示服务端数据\n
        - name: str
        - icon: str
        - recall: function
        """
        self.game_comp.CancelTimer(self.timer)
        # 首次更新
        storage_key = args["name"]
        self.TimerRequestUpdateDataScreen(storage_key)
        self.timer = self.game_comp.AddRepeatedTimer(1.0, self.TimerRequestUpdateDataScreen, storage_key)
        self.storage_menu.SetSwitchVisible(False)

    # -----------------------------------------------------------------------------------

    def HideAllMenuOption(self):
        """下拉框即将打开回调"""
        self.function_menu.SetSwitchVisible(False)
        self.storage_menu.SetSwitchVisible(False)
        self.module_menu.SetSwitchVisible(False)
        self.query_menu.SetSwitchVisible(False)

    # -----------------------------------------------------------------------------------

    """功能菜单"""

    # -----------------------------------------------------------------------------------

    """数据菜单"""

    def OnConfirmInputStorageKey(self, storage_key):
        """确认输入数据键回调"""
        self.mgr.server.CheckTargetAvailableStorageKey(self.local_id, storage_key)

    def TimerRequestUpdateDataScreen(self, key):
        """定时器请求更新数据界面"""
        self.mgr.server.GetTargetStorage(self.local_id, key)

    def OnResponseCheckStorageKey(self, key, available):
        # type: (str, bool) -> None
        """响应检测数据键是否有效"""
        if not available:
            self.SetTipMessage("数据键无效")
            return
        # 添加新的按键
        self.storage_menu.AddOption(key, callback=self.KeyRecallDisplayStorageData, insert=0)
        # 关闭输入弹窗
        self.mgr.pop_screen.SetInputPanelVisible(False)

    # -----------------------------------------------------------------------------------

    """内容界面"""

    def SetContextScreenVisible(self, visible):
        """设置内容界面"""
        if visible == self.visible_context_screen:
            return
        self.visible_context_screen = visible
        path = "/panel_debug/panel_win/context"
        self.SetVisible(path, self.visible_context_screen)
        path = "/panel_debug/panel_win/title/stack_options/button_hide"
        self.SetButtonLabel(path, "+" if not self.visible_context_screen else "-")
        if not self.visible_context_screen:
            self.SetScrollScreenVisible(False)

    """滚动文本界面"""

    def SetScrollScreenVisible(self, visible):
        # type: (bool) -> None
        """设置滚动文本界面显示"""
        if self.visible_scroll_screen == visible:
            return
        self.visible_scroll_screen = visible
        self.SetVisible("/panel_debug/panel_win/context/panel_scroll", self.visible_scroll_screen)
        if self.visible_scroll_screen:
            self.SetSettingScreenVisible(False)
            self.SetMakerScreenVisible(False)
            self.SetContextScreenVisible(True)
        elif self.timer:
            # 关闭定时器
            self.game_comp.CancelTimer(self.timer)
            self.timer = None

    def SetScrollText(self, context):
        """设置滚动列表内容"""
        self.SetMakerScreenVisible(False)
        self.SetContextScreenVisible(True)
        self.SetScrollScreenVisible(True)
        self.SetLabelText(self.scroll_text_path, context)

    # -----------------------------------------------------------------------------------

    """制作界面"""

    def SetMakerScreenVisible(self, visible):
        """制作界面显示"""
        if self.visible_maker_screen == visible:
            return
        self.visible_maker_screen = visible
        path = "/panel_debug/panel_win/context/panel_maker"
        self.SetVisible(path, self.visible_maker_screen)
        if self.visible_maker_screen:
            self.SetScrollScreenVisible(False)
            self.SetSettingScreenVisible(False)
            self.SetContextScreenVisible(True)
        elif self.preset_module.maker_screen:
            self.preset_module.maker_screen.SetActive(False)
            self.preset_module.maker_screen = None

    # -----------------------------------------------------------------------------------

    """设置界面"""

    def SetSettingScreenVisible(self, visible):
        """设置界面"""
        if visible == self.visible_setting_screen:
            return
        self.visible_setting_screen = visible
        self.SetVisible("/panel_debug/panel_win/context/panel_setting", self.visible_setting_screen)
        if self.visible_setting_screen:
            # 开启内容界面
            self.SetContextScreenVisible(True)
            self.SetScrollScreenVisible(False)
            self.SetMakerScreenVisible(False)

    # -----------------------------------------------------------------------------------

    """主界面"""

    def SetMainScreenVisible(self, visible):
        """设置总界面显示"""
        if self.visible_main_screen == visible:
            return
        self.visible_main_screen = visible
        self.SetVisible("/panel_debug/panel_win", self.visible_main_screen)
        if not self.visible_main_screen:
            # 关闭菜单
            self.function_menu.SetSwitchVisible(False)
            self.storage_menu.SetSwitchVisible(False)
            self.SetContextScreenVisible(False)
            self.SetSettingScreenVisible(False)
            self.SetMakerScreenVisible(False)
            # 关闭专注
            self.focus_mode = False
            self.comp_factory.CreateOperation(self.local_id).SetCanAll(True)
            self.game_comp.SimulateTouchWithMouse(False)

    def ToggleMainScreenVisible(self):
        """反转总界面显示"""
        self.SetMainScreenVisible(not self.visible_main_screen)
