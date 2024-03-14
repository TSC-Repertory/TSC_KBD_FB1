# -*- coding:utf-8 -*-


import weakref

from maker.render import RenderMakerScreen
from maker.skill import SkillMakerScreen
from maker.text_board import TextBoardMakerScreen
from ....client.entity import RawEntity
from ....client.system.base import ClientBaseSystem
from ....loader import MDKConfig
from ....ui.module import *


class PresetBase(ClientBaseSystem):
    """预设内容基类"""
    __mVersion__ = 3

    def __init__(self, ui, *args, **kwargs):
        super(PresetBase, self).__init__(MDKConfig.GetModuleClient(), *args, **kwargs)
        from root import OptionScreen
        self.ui = weakref.proxy(ui)  # type: OptionScreen

    def OnDestroy(self):
        del self.ui

    # -----------------------------------------------------------------------------------

    @property
    def ModuleSystem(self):
        return self.ui.ModuleSystem

    # -----------------------------------------------------------------------------------

    @property
    def timer(self):
        return self.ui.timer

    @timer.setter
    def timer(self, target):
        self.ui.timer = target

    @property
    def mgr(self):
        return self.ui.mgr

    # -----------------------------------------------------------------------------------

    @property
    def function_menu(self):
        # type: () -> MenuOptionComponent
        return self.ui.function_menu

    @property
    def storage_menu(self):
        # type: () -> MenuOptionComponent
        return self.ui.storage_menu

    @property
    def module_menu(self):
        # type: () -> MenuOptionComponent
        return self.ui.module_menu

    @property
    def query_menu(self):
        # type: () -> MenuOptionComponent
        return self.ui.query_menu

    # -----------------------------------------------------------------------------------

    def GetTargetId(self):
        # type: () -> str
        """获得目标Id"""
        if self.ui.selected_id and self.game_comp.IsEntityAlive(self.ui.selected_id):
            return self.ui.selected_id
        self.ui.selected_id = None
        return self.local_id

    def SetScrollText(self, context):
        # type: (str) -> None
        """设置滚动列表内容"""
        self.ui.SetScrollText(context)


class PresetFunction(PresetBase):
    """预设功能类"""
    __mVersion__ = 1

    def __init__(self, ui):
        super(PresetFunction, self).__init__(ui)
        self.state_pc_mode = False

    # 翻转电脑模式
    def TogglePcMode(self, _):
        """翻转电脑模式"""
        self.function_menu.SetSwitchVisible(False)
        self.state_pc_mode = not self.state_pc_mode
        clientApi.HidePauseGUI(self.state_pc_mode)
        clientApi.HideChatGUI(self.state_pc_mode)
        clientApi.HideReportGUI(self.state_pc_mode)
        clientApi.HideWalkGui(self.state_pc_mode)
        clientApi.HideJumpGui(self.state_pc_mode)
        clientApi.HideSneakGui(self.state_pc_mode)
        clientApi.HideChangePersonGui(self.state_pc_mode)
        clientApi.HideSwimGui(self.state_pc_mode)
        clientApi.HideMoveGui(self.state_pc_mode)
        clientApi.HideEmoteGUI(self.state_pc_mode)
        clientApi.HideFoldGUI(self.state_pc_mode)
        clientApi.SetHudChatStackVisible(not self.state_pc_mode)


class PresetData(PresetBase):
    """预设数据"""
    __mVersion__ = 1


class PresetModule(PresetBase):
    """预设模块"""
    __mVersion__ = 3

    def __init__(self, ui):
        super(PresetModule, self).__init__(ui)
        self.maker_screen = None
        self.skill_screen = None
        self.render_screen = None
        self.text_board_screen = None

    def OnDestroy(self):
        del self.maker_screen
        if self.skill_screen:
            self.skill_screen.OnDestroy()
            del self.skill_screen
        if self.render_screen:
            self.render_screen.OnDestroy()
            del self.render_screen
        if self.text_board_screen:
            self.text_board_screen.OnDestroy()
            del self.text_board_screen
        super(PresetModule, self).OnDestroy()

    # 技能模块回调
    def SkillMakerScreen(self, _):
        """技能模块回调"""
        if not self.skill_screen:
            self.skill_screen = SkillMakerScreen(self.mgr.ui_node)
        if self.skill_screen == self.maker_screen:
            return
        elif self.maker_screen:
            self.maker_screen.SetActive(False)
        self.skill_screen.SetActive(True)
        self.module_menu.SetSwitchVisible(False)
        self.ui.SetMakerScreenVisible(True)
        self.maker_screen = self.skill_screen

    # 渲染模块回调
    def RenderMakerScreen(self, _):
        """渲染模块回调"""
        if not self.render_screen:
            self.render_screen = RenderMakerScreen(self.mgr.ui_node)
        if self.render_screen == self.maker_screen:
            return
        elif self.maker_screen:
            self.maker_screen.SetActive(False)
        self.render_screen.SetActive(True)
        self.module_menu.SetSwitchVisible(False)
        self.ui.SetMakerScreenVisible(True)
        self.maker_screen = self.render_screen

    # 文字模块回调
    def TextBoardMakerScreen(self, _):
        """文字模块回调"""
        if not self.text_board_screen:
            self.text_board_screen = TextBoardMakerScreen(self.mgr.ui_node)
        if self.text_board_screen == self.maker_screen:
            return
        elif self.maker_screen:
            self.maker_screen.SetActive(False)
        self.text_board_screen.SetActive(True)
        self.module_menu.SetSwitchVisible(False)
        self.ui.SetMakerScreenVisible(True)
        self.maker_screen = self.text_board_screen


class PresetQuery(PresetBase):
    """预设查询"""
    __mVersion__ = 3

    def __init__(self, ui):
        super(PresetQuery, self).__init__(ui)

    def OnSelected(self):
        self.query_menu.SetSwitchVisible(False)
        self.game_comp.CancelTimer(self.timer)

    # 查询模块回调
    def QueryModule(self, _):
        """查询模块回调"""
        self.OnSelected()
        self.mgr.server.QueryServerModuleInfo(self.local_id)

    # 响应模块信息
    def OnResponseModuleInfo(self, server_module):
        # type: (dict) -> None
        """响应模块信息"""
        context = [
            "正在查询模块信息",
            "\n服务端模块："
        ]
        server_num = 0
        for module_key, version in server_module.iteritems():
            context.append("%s version: %s" % (module_key, version))
            server_num += 1
        context.append("\n客户端模块：")
        client_num = 0
        for module_key in self.ModuleSystem.GetAllModule():
            module_ins = self.ModuleSystem.GetModule(module_key)  # type: MDKConfig.GetModuleClientCls()
            context.append("%s version: %s" % (module_key, module_ins.GetVersion()))
            client_num += 1

        context.append("\n服务端共加载模块： %s" % server_num)
        context.append("客户端共加载模块： %s" % client_num)

        self.SetScrollText("\n".join(context))

    # 查询molang回调
    def QueryMolang(self, _):
        """查询molang回调"""
        self.OnSelected()

        module_key = MDKConfig.GetPresetModule().PropertyModuleClient.GetId()
        module = self.ModuleSystem.GetModule(module_key)  # type: MDKConfig.GetPresetModule().PropertyModuleClient
        if not module:
            self.SetScrollText("属性模块尚未启动")
            return

        def query():
            target_id = self.GetTargetId()
            storage = module.GetAllRegisterMolang(target_id)
            context = [
                "正在查询生物molang信息\n",
                "目标生物Id： %s <%s>" % (target_id, RawEntity.GetTypeStr(target_id)),
            ]
            number = 0
            for key, value in storage.iteritems():
                context.append("%s: %s" % (key, value))
                number += 1
            context.append("\n共注册molang： %s" % number)
            self.SetScrollText("\n".join(context))

        query()
        self.timer = self.game_comp.AddRepeatedTimer(0.1, query)

    # 查询属性回调
    def QueryAttribute(self, _):
        """查询属性回调"""
        self.OnSelected()

        module_key = MDKConfig.GetPresetModule().AttrModuleClient.GetId()
        module = self.ModuleSystem.GetModule(module_key)  # type: MDKConfig.GetPresetModule().AttrModuleClient
        if not module:
            self.SetScrollText("属性模块尚未启动")
            return
        self.SetScrollText("正在查询生物属性组信息")

        def query():
            target_id = self.GetTargetId()
            storage = module.GetEntityCache(self.local_id)  # type: dict
            context = [
                "正在查询生物属性组信息\n",
                "目标生物Id： %s <%s>" % (target_id, RawEntity.GetTypeStr(target_id)),
                "=" * 50,
            ]
            for group, data in storage.iteritems():
                context.append("group: 【%s】" % group)
                for key, value in data.iteritems():
                    context.append("    - %s: %s" % (key, value))
                context.append("=" * 50)
            self.SetScrollText("\n".join(context))

        query()
        self.timer = self.game_comp.AddRepeatedTimer(0.1, query)

    # 查询战利品回调
    def QueryLoot(self, _):
        """查询战利品回调"""
        self.OnSelected()

        module_key = MDKConfig.GetPresetModule().LootModuleClient.GetId()
        module = self.ModuleSystem.GetModule(module_key)  # type: MDKConfig.GetPresetModule().LootModuleClient
        if not module:
            self.SetScrollText("战利品模块尚未启动")
            return

        context = ["正在查询战利品信息\n"]
        self.SetScrollText("\n".join(context))
        # self.timer = self.game_comp.AddRepeatedTimer(0.1, query)

    # 查询任务回调
    def QueryQuest(self, _):
        """查询任务回调"""
        self.OnSelected()

        module_key = MDKConfig.GetPresetModule().QuestModuleClient.GetId()
        module = self.ModuleSystem.GetModule(module_key)  # type: MDKConfig.GetPresetModule().QuestModuleClient
        if not module:
            self.SetScrollText("战任务模块尚未启动")
            return

        context = ["正在查询任务信息\n"]
        self.SetScrollText("\n".join(context))
        # self.timer = self.game_comp.AddRepeatedTimer(0.1, query)

    # 查询配方回调
    def QueryRecipe(self, _):
        """查询配方回调"""
        self.OnSelected()

        context = ["正在查询配方信息\n"]
        self.SetScrollText("\n".join(context))
        # self.timer = self.game_comp.AddRepeatedTimer(0.1, query)
