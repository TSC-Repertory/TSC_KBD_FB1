# -*- coding:utf-8 -*-


from base import *


class SkillEnum(object):
    """技能枚举"""

    # 选项图标对应
    OptionIconMap = {
        "attack": "stone_sword",
        "projectile": "arrow",
        "detector": "armor_stand",
        "move": "feather",
        "timeline": "clock_item",
        "particle": "snowball",
        "unit": "banner_pattern"
    }

    @classmethod
    def GetOptionTexture(cls, option):
        # type: (str) -> str
        """获得选项图标路径"""
        return "textures/items/%s" % cls.OptionIconMap[option]


class SkillMakerScreen(MakerScreenBase):
    """技能制造界面"""
    __mVersion__ = 3

    def __init__(self, ui_node, **kwargs):
        super(SkillMakerScreen, self).__init__(ui_node, **kwargs)
        self.node_index = 0
        self.click_index = 0

        # 结点对应
        self.node_map = {}  # key: path
        # 菜单选项显示
        self.menu_option = None
        # 菜单选项显示
        self.visible_menu_option = False
        # 双击检测
        self.double_click_check = {}
        # 双击冷却
        self.double_click_cd = False

    def ConfigEvent(self):
        super(SkillMakerScreen, self).ConfigEvent()

    # -----------------------------------------------------------------------------------

    def KeyRecallMenuOption(self, args):
        """菜单按钮回调"""
        path = args["ButtonPath"]  # type: str
        node_type = path.split("/")[-2]
        self.CreateNewNode(node_type)
        self.SetMenuOptionVisible(False)

    # -----------------------------------------------------------------------------------

    def CreateNewNode(self, node_type):
        # type: (str) -> None
        """创建新的结点"""
        mould = "/panel_skill/panel_win"
        parent = "/panel_debug/panel_win/context/panel_maker"

        self.node_index += 1
        # 复制结点
        node_path = self.CloneComp(mould, parent, str(self.node_index))
        self.node_map[self.node_index] = node_path
        # 初始化结点
        skill_node = SkillNode(self, node_path, node_type)
        skill_node.Create()
        self.AddWinNode(node_path, skill_node)

    # -----------------------------------------------------------------------------------

    def OnWheelScrollDown(self):
        """鼠标滚轮向下调用"""
        print "[suc]", "OnWheelScrollDown"

    def OnWheelScrollUp(self):
        """鼠标滚轮向上调用"""
        print "[suc]", "OnWheelScrollUp"

    def OnMouseDoubleClick(self):
        """鼠标双击回调"""
        if not self.menu_option:
            parent = "/panel_debug/panel_win/context/panel_maker"
            target = "/panel_skill/panel_menu"
            self.menu_option = self.CloneComp(target, parent, "menu_option")
            parent = self.menu_option + "/image/panel_warp/stack_panel"
            mould = parent + "/mould"
            for key, item in SkillEnum.OptionIconMap.iteritems():
                option_path = self.CloneComp(mould, parent, key)
                self.SetLabelText(option_path, "New %s" % key.capitalize())
                image_path = option_path + "/image"
                self.SetImageSprite(image_path, "textures/items/%s" % item)
                button_path = option_path + "/button"
                self.SetButtonBind(button_path, self.KeyRecallMenuOption)
                self.SetVisible(option_path, True)
        self.SetMenuOptionVisible(True)

    # -----------------------------------------------------------------------------------

    def SetMenuOptionVisible(self, visible):
        # type: (bool) -> None
        """设置菜单按钮显示"""
        if visible == self.visible_menu_option or not self.menu_option:
            return
        self.visible_menu_option = visible
        self.SetVisible(self.menu_option, self.visible_menu_option)
        if self.visible_menu_option:
            touch_pos = Misc.GetPosModify(clientApi.GetTouchPos(), (0, -20))
            self.SetCompPos(self.menu_option, touch_pos)

    # -----------------------------------------------------------------------------------

    @check_active
    def MouseWheelClientEvent(self, args):
        self.OnWheelScrollUp() if args["direction"] else self.OnWheelScrollDown()

    @check_active
    def TapBeforeClientEvent(self, args):
        if self.visible_menu_option:
            self.SetMenuOptionVisible(False)
            self.double_click_check.clear()
        elif len(self.double_click_check) >= 1:
            self.OnMouseDoubleClick()
            for timer in self.double_click_check.values():
                self.game_comp.CancelTimer(timer)
            self.double_click_check.clear()
        else:
            self.click_index += 1
            timer = self.game_comp.AddTimer(0.2, lambda: self.double_click_check.pop(self.click_index, None))
            self.double_click_check[self.click_index] = timer
        args["cancel"] = True


class SkillNode(WinNode):
    """技能结点"""
    __mVersion__ = 2

    def __init__(self, mgr, path, node_type, **kwargs):
        super(SkillNode, self).__init__(mgr, path, node_type, **kwargs)
        self.mgr = weakref.proxy(mgr)  # type: SkillMakerScreen

        # 初始化显示
        icon_path = self.root + "/title/icon"
        self.SetImageSprite(icon_path, SkillEnum.GetOptionTexture(self.node_type))
        title_path = self.root + "/title/label"
        self.SetLabelText(title_path, self.node_type)
