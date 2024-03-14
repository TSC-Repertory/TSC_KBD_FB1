# -*- coding:utf-8 -*-


from base import *
from ...common.system.event import *


class UIPreset(ScreenNode, ModUIModuleBaseCls):
    """UI系统基类"""
    __mVersion__ = 7

    def __init__(self, namespace, name, param):
        super(UIPreset, self).__init__(namespace, name, param)
        ModUIModuleBaseCls.__init__(self, self, manual_listen=True)
        self.ui_node = self

        # pc文本
        self._pc_comp = set()

        # UI是否开启显示
        self._isUIOn = False
        # UI激活字典
        self.namespace = namespace
        # 添加UI实例信息
        self.AddUINode(self.namespace, self)

    def Create(self):
        """UI完成创建"""
        # 更新Pc组件修正显示
        self._UpdatePcComp()
        # 监听事件
        self.OnInit()
        # 发送创建完成事件
        print "[info]", "ui finished create: ", self.namespace
        self.NotifyToServer(UIEvent.OnUIScreenFinishedCreateEvent, {
            "playerId": self.local_id,
            "uiNode": self.namespace
        })
        self.BroadcastEvent(UIEvent.OnUIScreenFinishedCreateEvent, {
            "uiNode": self.namespace,
            "uiIns": self
        })

    def Update(self):
        """UI快循环"""

    def OnDestroy(self):
        self.BroadcastEvent(UIEvent.OnUINodeDestroyEvent, {"uiNode": self.namespace})
        super(UIPreset, self).OnDestroy()

    def Destroy(self):
        self.DelUINode(self.namespace)
        super(UIPreset, self).Destroy()

    # -----------------------------------------------------------------------------------

    @classmethod
    def PopScreen(cls):
        clientApi.PopScreen()

    @property
    def IsUIOn(self):
        """UI界面开启状态"""
        return self._isUIOn

    @classmethod
    def IsPcNode(cls):
        """是否为PC端"""
        return clientApi.GetPlatform() == 0

    # -----------------------------------------------------------------------------------

    def RegisterPcComp(self, config):
        # type: (list) -> None
        """
        注册随平台切换的文本\n
        - pc版Visible设置为True，其他平台False
        """
        self._pc_comp.update(set(config))

    def _UpdatePcComp(self):
        """更新显示"""
        if self.IsPcNode():
            for path in self._pc_comp:
                self.SetVisible(path, True)
        else:
            for path in self._pc_comp:
                self.SetVisible(path, False)

    # -----------------------------------------------------------------------------------

    def InitUIScreen(self):
        """初始化UI屏幕"""
        self._isUIOn = True
        self.SetScreenVisible(True)

    def CloseUIScreen(self):
        """关闭UI屏幕"""
        self._isUIOn = False
        self.SetScreenVisible(False)

    def ToggleUIScreen(self, mode=None):
        """设置反转开关UI屏幕"""
        if not isinstance(mode, bool):
            mode = not self._isUIOn
        self.InitUIScreen() if mode else self.CloseUIScreen()

    def PcMouseModify(self):
        """适配pc端鼠标"""
        if self.IsPcNode():
            self.game_comp.SimulateTouchWithMouse(True)

    # -----------------------------------------------------------------------------------

    def GetBaseUIControl(self, path):
        return ScreenNode.GetBaseUIControl(self, path)
