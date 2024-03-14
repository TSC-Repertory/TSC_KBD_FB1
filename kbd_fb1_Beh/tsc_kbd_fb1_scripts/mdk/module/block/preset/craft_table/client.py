# -*- coding:utf-8 -*-


from ...parts.client.base import LogicBlockClientBase
from .....common.system.base import *

if __name__ == '__main__':
    from server import LogicBlockCraftTableDoubleServer
    from ui import LogicBlockCraftTableUI


class LogicBlockCraftTableClient(LogicBlockClientBase):
    """合成台逻辑方块客户端"""
    __mVersion__ = 1

    def __init__(self, name, dim, pos):
        super(LogicBlockCraftTableClient, self).__init__(name, dim, pos)
        self.ui = None

    # -----------------------------------------------------------------------------------

    def OnDestroy(self):
        del self.ui
        super(LogicBlockCraftTableClient, self).OnDestroy()

    def OnFinishedLoadData(self):
        super(LogicBlockCraftTableClient, self).OnFinishedLoadData()
        # 开启绑定界面
        self.PushCreateUI(self._block_bind_ui, {"logic_block": self})

    def OnUISetExit(self):
        """退出界面时由界面调用"""
        # 关闭界面
        clientApi.PopScreen()
        # 服务端关闭逻辑方块
        self.NotifyToServer(UIEvent.OnUIExitBlockScreenEvent, {
            "playerId": self.local_id,
            "blockId": self.id
        })
        # 关闭逻辑方块
        self.ShuntDownBlock()

    def OnServerRequestShuntDown(self):
        # 关闭界面
        clientApi.PopScreen()

    # -----------------------------------------------------------------------------------

    """模块API"""

    # -----------------------------------------------------------------------------------

    @property
    def LogicUI(self):
        # type: () -> LogicBlockCraftTableUI
        """逻辑界面"""
        return self.ui


class LogicBlockCraftTableDoubleClient(LogicBlockCraftTableClient):
    """
    合成台逻辑方块双端客户端\n
    - 打开界面前需要拿到服务端的数据
    - 使用rpc通信
    """

    def __init__(self, name, dim, pos):
        super(LogicBlockCraftTableDoubleClient, self).__init__(name, dim, pos)
        self.rpc = None

    def OnDestroy(self):
        if self.rpc:
            self.rpc.Discard()
            del self.rpc
        super(LogicBlockCraftTableDoubleClient, self).OnDestroy()

    # -----------------------------------------------------------------------------------

    @property
    def server(self):
        # type: () -> LogicBlockCraftTableDoubleServer
        return self.rpc

    # -----------------------------------------------------------------------------------

    def OnFinishedLoadData(self):
        self.SynData()

    def OnUISetExit(self):
        # 关闭界面
        clientApi.PopScreen()
        # 服务端删除玩家
        self.server.DelPlayer(self.local_id)
        # 关闭逻辑方块
        self.ShuntDownBlock()

    def OnServerBlockAddPlayer(self, rpc, data):
        self.rpc = self.ModuleSystem.CreateRpcModule(self, rpc)
        # 开启绑定界面
        self.PushCreateUI(self._block_bind_ui, {"logic_block": self})
