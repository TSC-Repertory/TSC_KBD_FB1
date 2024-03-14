# -*- coding:utf-8 -*-


from const import *
from ..system.base import *

if __name__ == '__main__':
    from server import DebugModuleServer
    from ui.root import DebugScreen

"""
常用按键回调功能
- Tab: 鼠标模式切换

- Ctrl + F: 设置白天晴天
- Ctrl + G: 切换游戏模式

- Ctrl + D: 设置白天
- Ctrl + N: 设置晚上

- Ctrl + X: 清除个人背包
- Ctrl + C: 删除所有生物

- Alt + Z: 获得手持物品信息
- Alt + X: 获得指针方块信息
- Alt + C: 获得当前群系信息

- Del + |: 填充周围30格空气
"""


class DebugModuleClient(ModuleClientBase):
    """Debug模块客户端"""
    __mVersion__ = 22
    __identifier__ = ModuleEnum.identifier

    def __init__(self):
        super(DebugModuleClient, self).__init__()
        self.block_comp = self.comp_factory.CreateBlockInfo(clientApi.GetLevelId())

        self.rpc = self.ModuleSystem.CreateRpcModule(self, "debug")
        self.debug_ui = None

        self.state_toggle_mouse = False

        self.RegisterKeyPressRecall(KeyBoardType.KEY_TAB, self.OnKeyPressTab)
        self.RegisterKeyPressRecall(KeyBoardType.KEY_G, self.OnKeyPressG)
        self.RegisterKeyPressRecall(KeyBoardType.KEY_F, self.OnKeyPressF)
        self.RegisterKeyPressRecall(KeyBoardType.KEY_D, self.OnKeyPressD)
        self.RegisterKeyPressRecall(KeyBoardType.KEY_Z, self.OnKeyPressZ)
        self.RegisterKeyPressRecall(KeyBoardType.KEY_X, self.OnKeyPressX)
        self.RegisterKeyPressRecall(KeyBoardType.KEY_C, self.OnKeyPressC)
        self.RegisterKeyPressRecall(KeyBoardType.KEY_N, self.OnKeyPressN)
        self.RegisterKeyPressRecall(KeyBoardType.KEY_BACKSLASH, self.OnKeyPressBACKSLASH)

    def OnDestroy(self):
        self.UnRegisterKeyPressRecall(KeyBoardType.KEY_TAB, self.OnKeyPressTab)
        self.UnRegisterKeyPressRecall(KeyBoardType.KEY_G, self.OnKeyPressG)
        self.UnRegisterKeyPressRecall(KeyBoardType.KEY_F, self.OnKeyPressF)
        self.UnRegisterKeyPressRecall(KeyBoardType.KEY_D, self.OnKeyPressD)
        self.UnRegisterKeyPressRecall(KeyBoardType.KEY_Z, self.OnKeyPressZ)
        self.UnRegisterKeyPressRecall(KeyBoardType.KEY_X, self.OnKeyPressX)
        self.UnRegisterKeyPressRecall(KeyBoardType.KEY_C, self.OnKeyPressC)
        self.UnRegisterKeyPressRecall(KeyBoardType.KEY_N, self.OnKeyPressN)
        self.UnRegisterKeyPressRecall(KeyBoardType.KEY_BACKSLASH, self.OnKeyPressBACKSLASH)
        self.rpc.Discard()
        del self.rpc
        super(DebugModuleClient, self).OnDestroy()

    def ConfigEvent(self):
        super(DebugModuleClient, self).ConfigEvent()
        self.defaultEvent.update({
            ClientEvent.OnKeyPressInGame: self.OnKeyPressInGame,
            ClientEvent.UiInitFinished: self.UiInitFinished,
        })
        self.serverEvent.update({
            "ClientDebugStorage": self.ClientDebugStorage,
        })

    # -----------------------------------------------------------------------------------

    @property
    def server(self):
        # type: () -> DebugModuleServer
        return self.rpc

    def server_recall(self, recall):
        # type: (any) -> DebugModuleServer
        return self.rpc(recall)

    @property
    def ui(self):
        # type: () -> DebugScreen
        return self.debug_ui

    # -----------------------------------------------------------------------------------

    def SetClientSkin(self, path):
        self.local_player.SetSkin("skin/%s" % path)

    # -----------------------------------------------------------------------------------

    def GetBlockInfo(self):
        """获取方块信息"""
        pos = self.GetAimBlock().get("pos")
        if not pos:
            return
        info = self.block_comp.GetBlock(pos)
        block_info = info[0] + str(pos)
        self.SetTipMessage(block_info)
        print "[debug]", "block_info -> ", block_info

    # -----------------------------------------------------------------------------------

    def OnKeyPressTab(self):
        """反转鼠标模式"""
        self.state_toggle_mouse = not self.state_toggle_mouse
        self.game_comp.SimulateTouchWithMouse(self.state_toggle_mouse)

    def OnKeyPressG(self):
        """
        切换游戏模式\n
        - Ctrl + G
        """
        if self.GetKeyState(KeyBoardType.KEY_CONTROL):
            self.server.ToggleGameMode(self.local_id)

    def OnKeyPressF(self):
        """
        永远白天 + 晴天\n
        - Ctrl + F
        """
        if self.GetKeyState(KeyBoardType.KEY_CONTROL):
            self.server.SetCommands(self.local_id, ["/alwaysday", "/weather clear"])

    def OnKeyPressD(self):
        # 设置白天
        if self.GetKeyState(KeyBoardType.KEY_CONTROL):
            self.server.SetCommands(self.local_id, ["/time set day"])

    def OnKeyPressZ(self):
        # 获得手持物品信息
        if self.GetKeyState(KeyBoardType.KEY_MENU):
            itemDict = self.local_player.GetSelectedItem()
            if itemDict:
                for _index, item in enumerate(itemDict.items()):
                    print "[%s]" % _index, item[0], "->", item[1]
                print "=" * 50
                itemName = itemDict["newItemName"]  # type: str
                for _index, item in enumerate(self.Item.GetItemInfo(itemName).items()):
                    print "[%s]" % _index, item[0], "->", item[1]

    def OnKeyPressX(self):
        # 清除个人背包
        if self.GetKeyState(KeyBoardType.KEY_CONTROL):
            self.server.SetCommands(self.local_id, ["/clear @s"])
        # 获得指针方块信息
        if self.GetKeyState(KeyBoardType.KEY_MENU):
            self.GetBlockInfo()

    def OnKeyPressC(self):
        # 删除所有生物
        if self.GetKeyState(KeyBoardType.KEY_CONTROL):
            self.server.SetCommands(self.local_id, ["/cleanroom", "/title @s actionbar <cleanroom>"])
        # 获得当前群系信息
        elif self.GetKeyState(KeyBoardType.KEY_MENU):
            def display(res):
                print res

            self.server_recall(display).GetBiomeInfo(self.local_player.foot_pos, self.GetDimension())

    def OnKeyPressN(self):
        """
        设置晚上\n
        - Ctrl + N
        """
        if self.GetKeyState(KeyBoardType.KEY_CONTROL):
            self.server.SetCommands(self.local_id, ["/time set midnight"])

    def OnKeyPressBACKSLASH(self):
        """
        填充周围30格空气\n
         - Del + |
        """
        self.server.SetCommands(self.local_id, ["/fill ~-15~~-15 ~15~15~15 air"])

    # -----------------------------------------------------------------------------------

    def UiInitFinished(self, _):
        """界面初始化完成"""
        self.RegisterUI(ModuleUI.debug_key, ModuleUI.debug_config)
        self.CreateUI(ModuleUI.debug_key)

    def ClientDebugStorage(self, args):
        print "[suc]", "Client Storage"
        key = args["key"]
        if key:
            for k, v in self.GetPlayerStorage(key).iteritems():
                print "[warn]", "%s: %s" % (k, v)

    def OnKeyPressInGame(self, args):
        # type: (dict) -> None
        pack = copy.deepcopy(args)
        pack["playerId"] = self.local_id
        self.NotifyToServer(ClientEvent.OnKeyPressInGame, pack)
