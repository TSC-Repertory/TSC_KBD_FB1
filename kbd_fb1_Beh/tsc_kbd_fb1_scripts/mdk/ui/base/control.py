# -*- coding:utf-8 -*-


from mod.client.ui.screenNode import ScreenNode
from mod.common.minecraftEnum import TouchEvent

from ...client.system.base import *
from ...common.utils.misc import *


class TouchBind(clientApi.GetMinecraftEnum().TouchEvent):
    BindEnum = {
        # 按钮抬起时触发回调
        0: lambda comp, func: comp.SetButtonTouchUpCallback(func),
        # 按钮按下时触发回调
        1: lambda comp, func: comp.SetButtonTouchDownCallback(func),
        # 按钮按下后移出按钮范围抬起鼠标时触发回调
        3: lambda comp, func: comp.SetButtonTouchCancelCallback(func),
        # 按钮按下后移动鼠标触发回调
        4: lambda comp, func: comp.SetButtonTouchMoveCallback(func),
        # 鼠标按下后移入按钮触发回调
        5: lambda comp, func: comp.SetButtonTouchMoveInCallback(func),
        # 鼠标按下后移出按钮触发回调
        6: lambda comp, func: comp.SetButtonTouchMoveOutCallback(func),
        # 按钮所在画布退出时若鼠标仍未抬起时触发
        7: lambda comp, func: comp.SetButtonScreenExitCallback(func),
    }


class AnchorEnum(object):
    """锚点枚举"""
    TopLeft = "top_left"  # 相对于父节点的左上角
    TopMiddle = "top_middle"  # 相对于父节点的上边中间
    TopRight = "top_right"  # 相对于父节点的右上角
    LeftMiddle = "left_middle"  # 相对于父节点的左边中间
    Center = "center"  # 相对于父节点的中间
    RightMiddle = "right_middle"  # 相对于父节点的右边中间
    BottomLeft = "bottom_left"  # 相对于父节点的底部左边
    BottomMiddle = "bottom_middle"  # 相对于父节点的部中间
    BottomRight = "bottom_right"  # 相对于父节点的底部右边


class ModUIControlBase(object):
    """UI控件基类"""
    __mVersion__ = 6

    AnchorEnum = AnchorEnum

    def __init__(self, ui_node):
        self.ui_node = ui_node  # type: ScreenNode

        self._render_storage = {}

    def __del__(self):
        # print "[info]", "del:%s" % self.__class__.__name__
        pass

    def DestroyUI(self):
        """回收UI模块"""
        del self.ui_node

    # -----------------------------------------------------------------------------------

    def IsTouchInside(self, path, touchPos=None):
        # type: (str, tuple) -> bool
        """
        检测点击位置是否在组件内\n
        - 一般使用在按键触发事件内
        """
        if touchPos:
            touchX, touchY = touchPos
        else:
            touchX, touchY = map(int, clientApi.GetTouchPos())
        if touchX == 0 and touchY == 0:
            return False

        pos = self.GetFullPos(path)
        size = self.GetBaseUIControl(path).GetSize()
        if pos[0] <= touchX <= (pos[0] + size[0]) and pos[1] <= touchY <= (pos[1] + size[1]):
            return True
        return False

    # -----------------------------------------------------------------------------------

    def SetCompVisible(self, comp, visible=True):
        """设置控件显示"""
        if isinstance(comp, str):
            comp = self.GetBaseUIControl(comp)
        comp.SetVisible(visible)
        return comp

    def SetVisible(self, comp, visible=True):
        """设置控件显示"""
        if isinstance(comp, str):
            comp = self.GetBaseUIControl(comp)
        comp.SetVisible(visible)
        return comp

    def SetAlpha(self, comp, alpha):
        """
        设置节点的透明度\n
        - comp: str|BaseUIControl
        - alpha: float 透明度，0为完全透明
        """
        if isinstance(comp, str):
            comp = self.GetBaseUIControl(comp)
        comp.SetAlpha(1 - alpha)
        return comp

    def SetOpacity(self, comp, opacity):
        """
        设置节点不透明度\n
        - opacity: float 不透明度 1.0时为完全不透明
        """
        if isinstance(comp, str):
            comp = self.GetBaseUIControl(comp)
        comp.SetAlpha(1 - opacity)
        return comp

    def SetLayer(self, comp, layer):
        """设置控件层级"""
        if isinstance(comp, str):
            comp = self.GetBaseUIControl(comp)
        comp.SetLayer(layer)
        return comp

    def SetAnchor(self, comp, parent=None, target=None):
        # type: (any, str, str) -> None
        """设置锚点"""
        if isinstance(comp, str):
            comp = self.GetBaseUIControl(comp)
        if parent:
            comp.SetAnchorFrom(parent)
        if target:
            comp.SetAnchorTo(target)

    # -----------------------------------------------------------------------------------

    @staticmethod
    def GetCompPath(comp):
        # type: (any) -> str
        """获得组件的路径"""
        return comp if isinstance(comp, str) else getattr(comp, "mPath")

    def GetParentPath(self, comp):
        """获得组件父级路径"""
        if not isinstance(comp, str):
            comp = self.GetCompPath(comp)
        return "/".join(comp.split("/")[:-1])

    def GetCommonParent(self, comp1, comp2):
        """获得公共父级路径"""
        short_list = self.GetCompPath(comp1).split("/")
        long_list = self.GetCompPath(comp2).split("/")
        if len(short_list) > len(long_list):
            short_list, long_list = long_list, short_list
        for index, element in enumerate(short_list):
            if element != long_list[index]:
                return "/".join(short_list[:index])

    def GetCompInfo(self, comp):
        """
        获取组件的位置和尺寸  \n
        当组件隐藏的时候全是0 \n
        - comp: str|ButtonUIControl
        :return: (tuple->pos, tuple->size)
        """
        path = self.GetCompPath(comp)
        comp = self.GetBaseUIControl(path)
        return comp.GetPosition(), comp.GetSize()

    @staticmethod
    def _GetCompInfo(comp):
        """
        获取组件的位置和尺寸  \n
        当组件隐藏的时候全是0 \n
        - comp: ButtonUIControl
        :return: (tuple->pos, tuple->size)
        """
        return comp.GetPosition(), comp.GetSize()

    def SetCompPos(self, comp, pos, **kwargs):
        """设置控件位置"""
        if not kwargs:
            return self._SetCompPos(comp, pos)
        if isinstance(comp, str):
            comp = self.GetBaseUIControl(comp)
        # -----------------------------------------------------------------------------------
        followType = kwargs.get("follow")  # type: tuple
        if "px" in followType:
            comp.SetFullPosition("x", {"followType": "parent", "relativeValue": pos[0]})
        if "py" in followType:
            comp.SetFullPosition("y", {"followType": "parent", "relativeValue": pos[1]})

    def SetCompAxisPos(self, comp, axis, value):
        """这是控件一个轴的值"""
        if not isinstance(comp, str):
            comp = self.GetCompPath(comp)
        comp = self.GetBaseUIControl(comp)
        pos = comp.GetPosition()
        if axis == "x":
            res = (value, pos[1])
        else:
            res = (pos[0], value)
        comp.SetPosition(res)

    def _SetCompPos(self, comp, pos):
        """设置控件位置"""
        if isinstance(comp, str):
            comp = self.GetBaseUIControl(comp)
        comp.SetPosition(pos)

    def GetCompPos(self, comp):
        """获得组件位置"""
        path = self.GetCompPath(comp)
        comp = self.GetBaseUIControl(path)
        return comp.GetPosition()

    def GetFullPos(self, comp):
        """获得该组件的绝对坐标"""
        pathList = self.GetCompPath(comp).split("/")
        vector = Vector(0, 0)
        for index in xrange(1, len(pathList) + 1):
            newPath = "/".join(pathList[:index])
            if not newPath:
                continue
            tempPos = self.GetBaseUIControl(newPath).GetPosition()
            vector += tempPos
        return vector.ToTuple()

    def GetCompSize(self, comp):
        """获得组件尺寸"""
        if isinstance(comp, str):
            comp = self.GetBaseUIControl(comp)
        return comp.GetSize()

    def SetCompSize(self, comp, size, **kwargs):
        """设置控件尺寸"""
        if isinstance(comp, str):
            comp = self.GetBaseUIControl(comp)

        followType = kwargs.get("follow")  # type: tuple
        if not followType:
            return comp.SetSize(size, kwargs.get("resize_children", False))
        if "px" in followType:
            comp.SetFullSize("x", {"followType": "parent", "relativeValue": size[0]})
        elif "cx" in followType:
            comp.SetFullSize("x", {"followType": "children", "relativeValue": size[0]})
        elif "mcx" in followType:
            comp.SetFullSize("x", {"followType": "maxChildren", "relativeValue": 1.0})
        elif "sy" in followType:
            comp.SetFullSize("x", {"followType": "y", "relativeValue": size[0]})
        elif "fx" in followType:
            comp.SetFullSize("x", {"fit": True})
        # -----------------------------------------------------------------------------------
        if "py" in followType:
            comp.SetFullSize("y", {"followType": "parent", "relativeValue": size[1]})
        elif "cy" in followType:
            comp.SetFullSize("y", {"followType": "children", "relativeValue": size[0]})
        elif "mcy" in followType:
            comp.SetFullSize("y", {"followType": "maxChildren", "relativeValue": 1.0})
        elif "sx" in followType:
            comp.SetFullSize("y", {"followType": "x", "relativeValue": size[1]})
        elif "fy" in followType:
            comp.SetFullSize("y", {"fit": True})

    # -----------------------------------------------------------------------------------

    def GetCompCenterPos(self, comp):
        """获得控件中心位置"""
        size = self.GetCompSize(comp)
        return size[0] / 2.0, size[1] / 2.0

    def GetRelativeCenterPos(self, comp):
        """获得相对父级的中心点"""
        childSize = self.GetCompSize(comp)
        winPath = self.GetParentPath(comp)
        winSize = self.GetBaseUIControl(winPath).GetSize()

        # centerX = float(winSize[0] - float(float(childSize[0])) / 2) / 2
        centerX = float(winSize[0] - childSize[0]) / 2
        centerY = float(winSize[1] - childSize[1]) / 2

        return centerX, centerY

    # -----------------------------------------------------------------------------------

    def ResetAnim(self, comp):
        """重置控件动画"""
        if not isinstance(comp, str):
            comp = self.GetCompPath(comp)
        comp = self.GetBaseUIControl(comp)
        comp.SetVisible(False)
        comp.resetAnimation()
        comp.SetVisible(True)

    # -----------------------------------------------------------------------------------

    @staticmethod
    def JoinComp(parent, target):
        # type: (str, any) -> str
        """连接路径"""
        if not isinstance(target, list):
            target = [target]
        target.insert(0, parent)
        return "/".join(target)

    def CloneComp(self, target, parent, key):
        """
        克隆控件\n
        - 返回新控件路径
        """
        target_path = self.GetCompPath(target)
        parent_path = self.GetCompPath(parent)
        if self.ui_node.Clone(target_path, parent_path, key):
            return parent_path + "/" + key
        print "[error]", "克隆控件失败: %s" % key
        return ""

    def DelComp(self, comp):
        """删除控件"""
        target_path = self.GetCompPath(comp)
        parent_path = self.GetParentPath(comp)
        self.ui_node.RemoveComponent(target_path, parent_path)
        self.ui_node.UpdateScreen()

    # -----------------------------------------------------------------------------------

    def SetImageSprite(self, comp, texture):
        """设置图片控件的贴图"""
        path = self.GetCompPath(comp)
        comp = self.GetImageUIControl(path)
        comp.SetSprite(texture)
        return comp

    def SetButtonSprite(self, comp, default, pressed=None, hover=None):
        """设置按钮控件的图片"""
        if not isinstance(comp, str):
            comp = self.GetCompPath(comp)
        self.SetImageSprite(comp + "/default", default)
        if not pressed:
            pressed = default
        self.SetImageSprite(comp + "/pressed", pressed)
        if not hover:
            hover = pressed
        self.SetImageSprite(comp + "/hover", hover)
        return comp

    def SetProgressBarSprite(self, comp, empty, filled):
        if not isinstance(comp, str):
            comp = self.GetCompPath(comp)
        self.SetImageSprite(comp + "/empty_progress_bar", empty)
        self.SetImageSprite(comp + "/filled_progress_bar", filled)

    # -----------------------------------------------------------------------------------

    def GetBaseUIControl(self, path):
        return self.ui_node.GetBaseUIControl(path)

    def GetImageUIControl(self, path):
        return self.GetBaseUIControl(path).asImage()

    def GetLabelUIControl(self, path):
        return self.GetBaseUIControl(path).asLabel()

    def GetButtonUIControl(self, path):
        return self.GetBaseUIControl(path).asButton()

    def GetGridUIControl(self, path):
        return self.GetBaseUIControl(path).asGrid()

    def GetScrollViewUIControl(self, path):
        return self.GetBaseUIControl(path).asScrollView()

    def GetSwitchToggleUIControl(self, path):
        return self.GetBaseUIControl(path).asSwitchToggle()

    def GetTextEditBoxUIControl(self, path):
        return self.GetBaseUIControl(path).asTextEditBox()

    def GetProgressBarUIControl(self, path):
        return self.GetBaseUIControl(path).asProgressBar()

    def GetNeteasePaperDollUIControl(self, path):
        return self.GetBaseUIControl(path).asNeteasePaperDoll()

    def GetMiniMapUIControl(self, path):
        return self.GetBaseUIControl(path).asMiniMap()

    def GetSliderUIControl(self, path):
        return self.GetBaseUIControl(path).asSlider()

    def GetItemRendererUIControl(self, path):
        return self.GetBaseUIControl(path).asItemRenderer()

    def GetNeteaseComboBoxUIControl(self, path):
        return self.GetBaseUIControl(path).asNeteaseComboBox()

    def GetStackPanelUIControl(self, path):
        return self.GetBaseUIControl(path).asStackPanel()

    def GetInputPanelUIControl(self, path):
        return self.GetBaseUIControl(path).asInputPanel()

    # -----------------------------------------------------------------------------------

    def SetProgressBarValue(self, path, value):
        self.GetProgressBarUIControl(path).SetValue(value)

    def GetScrollContext(self, path):
        # type: (str) -> str
        return self.GetScrollViewUIControl(path).GetScrollViewContentPath()


class ModUIButtonControlCls(ModUIControlBase):
    """UI按钮控制类"""
    _hover_recall = {}

    def SetButtonBind(self, comp, recall, method=TouchEvent.TouchUp):
        """设置按钮的回调函数"""
        path = self.GetCompPath(comp)
        comp = self.GetButtonUIControl(path)
        comp.AddTouchEventParams({"isSwallow": True})
        TouchBind.BindEnum[method](comp, recall)
        return comp

    def SetButtonHoverBind(self, comp, in_recall=None, out_recall=None):
        """设置按钮的悬浮回调函数"""
        path = self.GetCompPath(comp)
        comp = self.GetButtonUIControl(path)
        comp.AddHoverEventParams()
        if callable(in_recall):
            comp.SetButtonHoverInCallback(in_recall)
        if callable(out_recall):
            comp.SetButtonHoverOutCallback(out_recall)

    def SetButtonHoverModifyBind(self, comp, recall):
        path = self.GetCompPath(comp)
        comp = self.GetButtonUIControl(path)
        comp.AddHoverEventParams()
        self._hover_recall[path] = recall
        comp.SetButtonHoverInCallback(self._PresetHoverRecall)
        comp.SetButtonHoverOutCallback(self._PresetHoverRecall)

    def _SetButtonBind(self, path, func, method=TouchEvent.TouchUp, swallow=True):
        """设置按钮的回调函数"""
        comp = self.GetButtonUIControl(path)
        comp.AddTouchEventParams({"isSwallow": swallow})
        TouchBind.BindEnum[method](comp, func)
        return comp

    def SetButtonState(self, comp, active, gray=False):
        """
        设置按钮是否启用\n
        - active: bool 是否启用
        - gray: bool 是否启用置灰
        """
        path = self.GetCompPath(comp)
        button = self.GetButtonUIControl(path)
        button.GetChildByName("default").asImage().SetSpriteGray(not active and gray)
        button.SetTouchEnable(active)
        return button

    def SetButtonGray(self, comp, gray=False, effect=3):
        """
        设置按钮图片灰色\n
        - comp: 按钮控件
        - gray: bool 是否置灰
        - effect: num 影响数量（3为全部按钮图片影响）
        """
        path = self.GetCompPath(comp)
        button = self.GetButtonUIControl(path)
        button.GetChildByName("default").asImage().SetSpriteGray(gray)
        if effect >= 2:
            button.GetChildByName("pressed").asImage().SetSpriteGray(gray)
        if effect >= 3:
            button.GetChildByName("hover").asImage().SetSpriteGray(gray)

    def SetButtonLabel(self, comp, text):
        """设置编辑器按钮的文本内容"""
        if not isinstance(comp, str):
            comp = self.GetCompPath(comp)
        path = comp + "/button_label"
        self.GetLabelUIControl(path).SetText(text)

    # -----------------------------------------------------------------------------------

    def _PresetHoverRecall(self, args):
        path = args["ButtonPath"]
        recall = self._hover_recall.get(path)
        if not recall:
            return
        return recall(path, args["isHoverIn"] == 1)


class ModUILabelControlCls(ModUIControlBase):
    """UI文本控制类"""
    __mVersion__ = 2

    def SetLabelText(self, path, text):
        """设置文本控件文本"""
        label = self.GetLabelUIControl(path)
        label.SetText(str(text))
        return label

    def SetLabelFontSize(self, path, size):
        """
        设置文本字体大小\n
        - 缺参数是api问题
        """
        self.GetLabelUIControl(path).SetTextFontSize(size)


class ModUIImageControlCls(ModUIControlBase):
    """UI图形控制类"""
    __mVersion__ = 3
    _clipDirectionMap = {
        0: "fromBottomToTop",
        1: "fromLeftToRight",
        2: "fromRightToLeft",
        3: "fromOutsideToInside",
        4: "fromTopToBottom"
    }

    def GetClipDirection(self, mode):
        # type: (int) -> str
        """获得裁剪方向对应"""
        default = self._clipDirectionMap.get(0)
        return self._clipDirectionMap.get(mode, default)

    def SetRenderItem(self, comp, item):
        """设置物品渲染控件的渲染物品"""
        if not isinstance(item, dict):
            item = {"newItemName": item, "count": 1}
        if isinstance(comp, str):
            path = comp
            comp = self.GetItemRendererUIControl(comp)
        else:
            path = self.GetCompPath(comp)
        comp.SetUiItem(item.get("newItemName"), item.get("newAuxValue", 0), item.get("enchant", False))
        self._render_storage[path] = item
        return comp

    def SetRenderGridSlot(self, comp, item, use_count=True):
        """
        网格按钮物品渲染\n
        - 一般用于背包网格物品
        - 传入为按键路径
        """
        render = comp + "/item_renderer"
        self._render_storage[render] = item
        if not item:
            self.GetBaseUIControl(render).SetVisible(False)
        elif isinstance(item, str):
            item = {"newItemName": item, "count": 1}
        comp = self.GetItemRendererUIControl(render)
        comp.SetUiItem(item["newItemName"], item.get("newAuxValue", 0), item.get("enchant", False))
        comp.SetVisible(True)
        path = render + "/label"
        if use_count:
            count = item.get("count", 0)
            if count <= 1:
                count = ""
            self.GetLabelUIControl(path).SetText("%s" % count)

    def SetRenderGridRenderer(self, comp, item, use_count=True):
        """
        物品渲染\n
        - 一般用于拖拽物的渲染
        - 传入为物品渲染控件的路径
        - 可一起设置物品数量
        """
        self._render_storage[comp] = item
        if not item:
            render = self.GetBaseUIControl(comp)
            render.SetVisible(False)
            return render
        else:
            render = self.GetItemRendererUIControl(comp)
            render.SetUiItem(item["newItemName"], item.get("newAuxValue", 0), item.get("enchant", False))
            render.SetVisible(True)
            if use_count:
                count = item.get("count", 0)
                if count <= 1:
                    count = ""
                self.GetLabelUIControl(comp + "/label").SetText("%s" % count)
            return render

    def GetRenderGridSlotItem(self, comp):
        # type: (str) -> dict
        render = comp + "/item_renderer"
        return self.GetRenderItem(render)

    def GetRenderItem(self, comp):
        # type: (any) -> dict
        """
        获取物品渲染控件的渲染物品\n
        - 不使用SetRenderItem设置将无缓存
        """
        if not isinstance(comp, str):
            comp = self.GetParentPath(comp)
        return self._render_storage.get(comp)

    def SetRenderUIItemMap(self, comp, item):
        """设置物品渲染控件的UI渲染物品对应"""
        if isinstance(comp, str):
            path = comp
        else:
            path = self.GetCompPath(comp)
        self._render_storage[path] = item

    def SetImageGray(self, comp, gray):
        """设置图片置灰"""
        if isinstance(comp, str):
            comp = self.GetImageUIControl(comp)
        comp.SetSpriteGray(gray)

    def SetImageColor(self, comp, color):
        """设置图片颜色"""
        if isinstance(comp, str):
            comp = self.GetImageUIControl(comp)
        comp.SetSpriteColor(color)

    def SetImageUV(self, path, uv):
        # type: (str, tuple) -> None
        """设置图像uv"""
        self.GetImageUIControl(path).SetSpriteUV(uv)

    def SetImageUVSize(self, path, size):
        self.GetImageUIControl(path).SetSpriteUVSize(size)


class ModUIMoveControlCls(ModUIButtonControlCls, ModUIImageControlCls, ModUILabelControlCls):
    """UI形变控制类"""
    __mVersion__ = 2

    def __init__(self, ui_node):
        ModUIControlBase.__init__(self, ui_node)

    def GetCompScaleGen(self, comp, start, end, duration, recall=None):
        """设置控件大小变化"""
        path = self.GetCompPath(comp)
        comp = self.GetBaseUIControl(path)

        def active():
            for i in xrange(duration + 1):
                yield 1
                rate = float(i) / duration
                size = Misc.GetTupleFromRate(rate, start, end)
                comp.SetSize(size, True)
            if callable(recall):
                recall()

        return active

    def GetCompMoveGen(self, comp, start, end, duration):
        """设置控件在从某点移至某一点"""
        path = self.GetCompPath(comp)
        comp = self.GetBaseUIControl(path)

        def active():
            for i in xrange(duration + 1):
                yield 1
                rate = float(i) / duration
                pos = Misc.GetTupleFromRate(rate, start, end)
                comp.SetPosition(pos)

        return active

    def GetCompCenterScale(self, comp, start, end, duration):
        """设置控制以中间缩放[未测试]"""
        path = self.GetCompPath(comp)
        comp = self.GetBaseUIControl(path)
        full_size = comp.GetSize()

        def active():
            for i in xrange(duration + 1):
                yield 1
                rate = float(i) / duration
                size = Misc.GetTupleFromRate(rate, start, end)
                del_size = Misc.GetPosModify(full_size, size, method="sub")
                pos = Misc.GetPosModify(comp.GetPosition(), (del_size[0] / 2, del_size[1] / 2))
                comp.SetPosition(pos)
                comp.SetSize(size, True)

        return active

    def GetCompAlphaGen(self, comp, start, end, duration):
        """获得获得透明度变化生成器"""
        path = self.GetCompPath(comp)
        comp = self.GetBaseUIControl(path)

        def active():
            for i in xrange(duration + 1):
                yield 1
                rate = float(i) / duration
                value = Misc.GetValueFromRate(rate, start, end)
                comp.SetAlpha(value)

        return active

    def SetAnimScale(self, comp, start, end, duration):
        # type: (any, tuple, tuple, float) -> None
        """设置控件在原位置缩放"""
        path = self.GetCompPath(comp)
        comp = self.GetBaseUIControl(path)

        def active():
            comp.SetSize(start)
            maxRange = int(duration * 30)
            for i in xrange(1, maxRange + 1):
                rate = float(i) / maxRange
                scale = Misc.GetTupleFromRate(rate, start, end)
                comp.SetSize(scale)
                center = self.GetRelativeCenterPos(comp)
                comp.SetPosition(center)
                yield 1

        MDKConfig.GetModuleClient().StartCoroutine(active)

    def GetCompFontSizeGen(self, comp, start, end, duration, recall=None):
        """获得文字大小变化生成器"""
        comp = self.GetLabelUIControl(comp)

        def active():
            for i in xrange(duration + 1):
                yield 1
                rate = float(i) / duration
                value = Misc.GetValueFromRate(rate, start, end)
                comp.SetTextFontSize(value)
            if callable(recall):
                try:
                    recall()
                except Exception as e:
                    print "[error]", e

        return active
