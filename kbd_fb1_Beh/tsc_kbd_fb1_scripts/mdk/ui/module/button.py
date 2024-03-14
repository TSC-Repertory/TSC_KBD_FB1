# -*- coding:utf-8 -*-


from base import UIModuleBase
from ..system.preset import *


class ButtonRecallMgr(UIModuleBase):
    """
    按键回调管理\n

    无法回收问题：
    - 猜想网易创建按钮回调后会缓存路径和实例对应，然后没删
    """
    __mVersion__ = 1

    def __init__(self, ui_node, **kwargs):
        super(ButtonRecallMgr, self).__init__(ui_node, **kwargs)
        self._comp_bind_storage = {}
        self._touch_recall_map = {
            TouchEvent.TouchUp: {},
            TouchEvent.TouchDown: {},
            TouchEvent.TouchCancel: {},
            TouchEvent.TouchMove: {},
            TouchEvent.TouchMoveIn: {},
            TouchEvent.TouchMoveOut: {},
            TouchEvent.TouchScreenExit: {},
        }

    def OnDestroy(self):
        del self._touch_recall_map
        del self._comp_bind_storage
        super(ButtonRecallMgr, self).OnDestroy()

    # -----------------------------------------------------------------------------------

    def DestroyCompBind(self, comp):
        # type: (str) -> None
        """清除组件的绑定"""
        comp_set = self._comp_bind_storage.pop(comp, None)  # type: set
        if comp_set:
            for method in list(comp_set):
                self._touch_recall_map[method].pop(comp, None)

    def SetButtonBind(self, comp, recall, method=TouchEvent.TouchUp, swallow=True):
        if not callable(recall):
            print "[warn]", "Invalid button recall: %s" % comp
            return None
        path = self.GetCompPath(comp)
        if path not in self._comp_bind_storage:
            self._comp_bind_storage[path] = set()
        comp_set = self._comp_bind_storage[path]  # type: set
        comp_set.add(method)

        comp = self.GetButtonUIControl(path)
        comp.AddTouchEventParams({"isSwallow": swallow})
        self._touch_recall_map[method][path] = recall
        TouchBind.BindEnum[method](comp, self._KeyRecallBind)
        return comp

    def _KeyRecallBind(self, args):
        path = args["ButtonPath"]
        method = args["TouchEvent"]
        recall = self._touch_recall_map[method].get(path)
        if recall:
            recall(args)


class HudButtonMgr(UIModuleBase):
    """
    按钮管理模块\n
    - 技能CD冷却
    - 按键拖动、重置
    ----------------\n
    - 问题：无法回收模块
    - 需要解决多包下的 __storageKey重复问题
    ----------------\n
    遮罩UI需要包含层级：\n
    -- image_mask  # 遮罩黑图 默认透明度设置为0
    --- label_mask  # 遮罩CD
    """
    __mVersion__ = 10
    __storageKey = MDKConfig.ModuleNamespace + "ButtonStorage"

    def __init__(self, ui_node, **recallMap):
        super(HudButtonMgr, self).__init__(ui_node)
        self._mask_map = {}  # str->buttonPath: ImageUIControl
        self._label_map = {}  # str->buttonPath: LabelUIControl
        self._recall_up_map = {}
        self._recall_down_map = {}
        for path, recall in recallMap.iteritems():
            if isinstance(recall, tuple):
                if recall[1] == TouchEvent.TouchDown:
                    self._recall_down_map[path] = recall[0]
                    self._SetButtonBind(path, self._KeyRecallDownEvent, TouchEvent.TouchDown)
                    continue
            else:
                self._recall_up_map[path] = recall
                self._SetButtonBind(path, self._KeyRecallUpEvent, TouchEvent.TouchUp)
        # -----------------------------------------------------------------------------------
        """遮罩冷却相关"""
        self._skill_cd = {}  # str->buttonPath: {"pre": int, "max": int}
        # -----------------------------------------------------------------------------------
        """控件拖动相关"""
        self._drag_target = None
        self._drag_mode = False
        self._can_drag = set()  # {str, }
        self._reset_drag = {}  # str: tuple
        self._modify_drag = {}  # str: tuple
        self._dragMap = {}  # str: str
        self._dragStorageKey = self.__storageKey + ui_node.namespace

    def OnDestroy(self):
        del self._recall_up_map
        del self._recall_down_map
        del self._mask_map
        del self._label_map
        del self._skill_cd
        del self._dragMap
        del self._reset_drag
        del self._modify_drag
        del self._can_drag
        super(HudButtonMgr, self).OnDestroy()

    def ConfigEvent(self):
        super(HudButtonMgr, self).ConfigEvent()
        self.defaultEvent[ClientEvent.OnScriptTickClient] = self._OnScriptTickClient
        self.serverEvent[ServerEvent.RequestHUDKeyModify] = self._RequestHUDKeyModify

    # -----------------------------------------------------------------------------------

    """遮罩冷却相关Api"""

    def IsButtonCd(self, path):
        # type: (str) -> bool
        """
        判断是否正处于冷却状态\n
        - 设计用于使用响应本次按键\n
        - 一般放在按键回调开头
        """
        return self._skill_cd.get(path) is not None

    def AddButtonCd(self, path, cd=0.1):
        # type: (str, int) -> None
        """
        设置技能CD遮罩显示\n
        - 常用于技能按键回调，或有CD的按键\n
        - 使用前需要包含目标控件与recallMap字典里
        """

        # 设置技能CD
        self._skill_cd[path] = {"pre": cd, "max": cd}
        # 获取遮罩
        if not self._mask_map.get(path):
            # -----------------------------------------------------------------------------------
            """尝试获得遮罩控件"""
            maskPath = self.GetCompPath(path) + "/image_mask"
            try:
                mask = self.GetImageUIControl(maskPath)
                self._mask_map[path] = mask
            except AttributeError:
                # print "[error]", "无法获得遮罩控件：%s" % maskPath
                return
            # -----------------------------------------------------------------------------------
            """尝试获得文本控件"""
            labelPath = maskPath + "/label_mask"
            try:
                label = self.GetLabelUIControl(labelPath)
                self._label_map[path] = label
            except AttributeError:
                # print "[error]", "无法获得遮罩文本控件：%s" % labelPath
                return

    # -----------------------------------------------------------------------------------

    """拖拽相关Api"""

    def GetDragMode(self):
        # type: () -> bool
        """获得拖动状态"""
        return self._drag_mode

    def SetDragMode(self, mode):
        # type: (bool) -> None
        """
        设置拖动模式\n
        - 设计是否开启按键调节模式
        - 一般用于某个开关按键回调处
        - 建议使用<ToggleDragMode>反转状态
        """
        self._drag_mode = mode
        if not mode:
            self.SetLocalConfigData(self._dragStorageKey, self._modify_drag)

    def ToggleDragMode(self):
        # type: () -> bool
        """
        翻转拖动模式\n
        - 设计是否开启按键调节模式
        - 一般用于某个开关按键回调处
        """
        mode = not self._drag_mode
        self.SetDragMode(mode)
        return mode

    def SetDraggable(self, comp, isOn=True):
        """
        配置可拖动的按钮控件\n
        - 单独设置某个按键是否可拖动
        - 关闭后已注册的按钮监听不会注销，但不影响使用
        """
        path = self.GetCompPath(comp)
        if not isOn:
            """关闭"""
            self._can_drag.discard(path)
        else:
            self._can_drag.add(path)
            # 调用时只运行一次
            target = self._GetDragTarget(path)
            if not self._reset_drag.get(target):
                if not self._recall_down_map.get(path):
                    self._SetButtonBind(path, self._KeyRecallDownEvent, TouchEvent.TouchDown)
                self._reset_drag[target] = self.GetCompPos(target)
                # 如果没有抬起回调
                if not self._recall_up_map.get(path):
                    self._SetButtonBind(path, self._KeyRecallUpEvent, TouchEvent.TouchUp)
                    self._recall_up_map[path] = self._RecallVoid

    def SetDraggableList(self, drag_list):
        # type: (list) -> None
        """
        配置可拖动的按钮控件\n
        - 设置列表里组件可拖动
        - 一般用于初始化某块后调用
        """
        for path in drag_list:
            self.SetDraggable(path, True)

    def SetDragMap(self, comp, target):
        # type: (str, str) -> None
        """
        设置拖拽对应修整\n
        - 当按下comp按钮后，拖拽target的控件
        - 可用于类似情况：多个控件组成的panel，但由里面某个button控制整个拖拽
        - 举例：HUD的角色状态栏，通过点击头像按钮拖动整个状态栏
        """
        self._dragMap[comp] = target

    def SetDragMapBatch(self, config):
        # type: (dict) -> None
        """批量设置拖拽对应"""
        for comp, target in config.iteritems():
            self.SetDragMap(comp, target)

    def UpdateKeyConfig(self):
        """更新按键配置"""
        config = self.GetLocalConfigData(self._dragStorageKey)
        if not config:
            return
        # -----------------------------------------------------------------------------------
        self._modify_drag = config

        for path, pos in self._modify_drag.iteritems():
            target = self._GetDragTarget(path)
            self.GetBaseUIControl(target).SetPosition(tuple(pos))

    def ResetDragInfo(self, comp):
        """
        重置某控件的拖动位置\n
        - 一般用于重置布局按钮回调或服务端指令请求
        """
        path = self.GetCompPath(comp)
        target = self._GetDragTarget(path)
        pos = self._reset_drag.get(target)
        if pos:
            self.GetBaseUIControl(target).SetPosition(pos)
            self._modify_drag[target] = pos

    def ResetAllDragInfo(self):
        """
        重置所有控件拖动位置\n
        - 一般用于重置布局按钮回调或服务端指令请求
        """
        for path, pos in self._reset_drag.iteritems():
            target = self._GetDragTarget(path)
            self.GetBaseUIControl(target).SetPosition(pos)
            self._modify_drag[target] = pos
        self.SetLocalConfigData(self._dragStorageKey, self._modify_drag)

    # -----------------------------------------------------------------------------------

    def _OnScriptTickClient(self):
        if not self._active:
            return
        # -----------------------------------------------------------------------------------
        """拖动逻辑"""
        if self._drag_mode and self._drag_target:
            touchX, touchY = clientApi.GetTouchPos()
            if touchX and touchY:
                # -----------------------------------------------------------------------------------
                """获取控件中心位置"""
                target = self._GetDragTarget(self._drag_target)
                comp = self.GetBaseUIControl(target)
                pos, size = self._GetCompInfo(comp)
                centerX, centerY = touchX - (size[0] / 2), touchY - (size[1] / 2)
                # -----------------------------------------------------------------------------------
                comp.SetPosition((centerX, centerY))
                # 保存拖动位置
                self._modify_drag[target] = (centerX, centerY)
            else:
                self._drag_target = None
        # -----------------------------------------------------------------------------------
        """冷却遮罩逻辑"""
        for path, config in self._skill_cd.items():
            assert isinstance(config, dict)
            preValue = config.get("pre")  # type: int
            preValue -= 1
            config["pre"] = preValue
            mask = self._mask_map.get(path)
            if preValue <= 0:
                self._skill_cd.pop(path, None)
                if mask:
                    self.SetAlpha(mask, 1)
            else:
                maxValue = config.get("max")
                # -----------------------------------------------------------------------------------
                """透明度显示"""
                if not mask:
                    continue
                rate = float(preValue) / maxValue
                self.SetAlpha(mask, 1 - rate)
                # -----------------------------------------------------------------------------------
                """文字显示"""
                label = self._label_map.get(path)
                if not label:
                    continue
                text = round(rate * maxValue / 30, 1)
                text = "%ss" % text if text != 0 else ""
                label.SetText(text)

    def _KeyRecallUpEvent(self, args):
        # type: (dict) -> None
        """按钮统一按下回调"""
        buttonPath = args.get("ButtonPath")
        # -----------------------------------------------------------------------------------
        """按键拖动"""
        if self._drag_mode and buttonPath == self._drag_target:
            self._drag_target = None
            return
        # -----------------------------------------------------------------------------------
        """按键回调"""
        recall = self._recall_up_map.get(buttonPath)
        if callable(recall):
            recall(args)

    def _KeyRecallDownEvent(self, args):
        # type: (dict) -> None
        """按钮统一按下回调"""
        buttonPath = args.get("ButtonPath")
        """按键拖动"""
        if self._drag_mode and buttonPath in self._can_drag:
            self._drag_target = buttonPath
        # -----------------------------------------------------------------------------------
        """按键回调"""
        recall = self._recall_down_map.get(buttonPath)
        if callable(recall):
            recall(args)

    def _RequestHUDKeyModify(self, args):
        # type: (dict) -> None
        """请求修正按钮事件"""
        if args.get("reset"):
            self.ResetAllDragInfo()

    def _GetDragTarget(self, target):
        """获得拖拽目标"""
        return self._dragMap.get(target, target)

    def _RecallVoid(self, args):
        # type: (dict) -> None
        """空回调"""


class MenuOptionComponent(UIModuleBase):
    """菜单选项控件"""
    __mVersion__ = 4

    def __init__(self, ui_node, path, **kwargs):
        super(MenuOptionComponent, self).__init__(ui_node, **kwargs)
        self._gen_index = 0
        self.recall_map = []  # [{"name": str, "icon": str, "callback": func}]
        self.button_map = []  # panel_path
        self.gen = {}

        self._button_path = path
        self._image_path = path + "/options"

        self._recall_will_open = None
        self._recall_on_open = None
        self._recall_on_close = None

        self.SetButtonBind(self._button_path, self.KeyRecallSwitcher)

        # 下拉显示
        self.visible_switch = False

        self.SetSwitchVisible(False)

    def __del__(self):
        print "[warn]", "del component:", self.__class__.__name__

    def OnDestroy(self):
        for gen in self.gen.items():
            self.StopCoroutine(gen)
        del self.gen
        del self.button_map
        del self._recall_on_open
        del self._recall_on_close
        super(MenuOptionComponent, self).OnDestroy()

    # -----------------------------------------------------------------------------------

    def KeyRecallSwitcher(self, _):
        # type: (dict) -> None
        """开关按钮"""
        if self.gen.get("switch"):
            return
        self.ToggleSwitchVisible()

    def KeyRecallOptions(self, args):
        button = args["ButtonPath"]  # type: str
        path = "/".join(button.split("/")[:-2])
        index = self.button_map.index(path)
        config = self.recall_map[index]
        if not config:
            return
        callback = config["callback"]
        if callable(callback):
            callback(config)

    # -----------------------------------------------------------------------------------

    def SetSwitchVisible(self, visible):
        """设置下拉选项显示"""
        if visible == self.visible_switch:
            return
        self.gen["switch"] = self.StartCoroutine(self.StartSwitchAim(visible), lambda: self.gen.pop("switch", None))

    def StartSwitchAim(self, visible):
        # type: (bool) -> None
        """显示下拉选项"""
        if not visible:
            for index in xrange(len(self.button_map), 0, -1):
                path = self.button_map[index - 1]
                self.SetVisible(path, False)
                # yield 1
            self.SetVisible(self._image_path, False)
            if callable(self._recall_on_close):
                self._recall_on_close()
        else:
            if callable(self._recall_will_open):
                self._recall_will_open()
            self.SetVisible(self._image_path, True)
            for index in xrange(len(self.button_map)):
                path = self.button_map[index]
                self.SetVisible(path, True)
                # yield 1
            if callable(self._recall_on_open):
                self._recall_on_open()
        self.visible_switch = visible
        yield 0

    def ToggleSwitchVisible(self):
        """反转显示下拉选项"""
        self.gen["switch"] = self.StartCoroutine(
            self.StartSwitchAim(not self.visible_switch),
            lambda: self.gen.pop("switch", None)
        )

    # -----------------------------------------------------------------------------------

    def SetMenuTitle(self, text):
        # type: (str) -> None
        """设置按钮标题"""
        self.SetLabelText(self._button_path + "/label", text)

    def GetOptionCount(self):
        # type: () -> int
        """获得选项数量"""
        return len(self.button_map)

    # -----------------------------------------------------------------------------------

    def AddOption(self, name="New Button", icon="textures/items/feather", callback=None, insert=-1):
        # type: (str, str, any, int) -> None
        """
        添加选项\n
        返回按钮路径\n
        - name: str 按钮名称
        - icon: str 按钮图标
        - callback: func 回调函数，默认传入按钮路径
        - insert: int 插入列表索引
        """
        parent = self._image_path + "/stack_panel"
        mould = parent + "/panel"
        self._gen_index += 1
        new_panel = self.CloneComp(mould, parent, str(self._gen_index))
        self.SetVisible(new_panel, True)
        button = new_panel + "/label/button"
        self.SetButtonBind(button, self.KeyRecallOptions)
        self.button_map.append(new_panel)
        self.recall_map.insert(insert, {"name": name, "icon": icon, "callback": callback})

        # 更新按钮渲染
        for index, path in enumerate(self.button_map):
            config = self.recall_map[index]  # type: dict
            self.SetLabelText(path + "/label", config["name"])
            self.SetImageSprite(path + "/label/image", config["icon"])

    def DelOptionByPath(self, path):
        # type: (str) -> bool
        """删除选项 - 根据按钮路径"""
        path = "/".join(path.split("/")[:-2])
        if path not in self.button_map:
            return False
        index = self.button_map.index(path)
        self.DelComp(path)
        self.button_map.pop(index)
        self.recall_map.pop(index)
        # todo: 反监听按钮
        return True

    def RegisterWillOpenMenuCallBack(self, callback):
        """注册即将打开下拉框时回调"""
        self._recall_will_open = callback

    def RegisterOpenMenuCallback(self, callback):
        """注册展开下拉框事件回调"""
        self._recall_on_open = callback

    def RegisterCloseMenuBoxCallback(self, callback):
        """注册关闭下拉框事件回调"""
        self._recall_on_close = callback
