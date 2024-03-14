# -*- coding:utf-8 -*-


import copy

from ...const import ModuleEvent
from ...parts.server.base import LogicBlockServerBase
from .....common.utils.misc import Misc

if __name__ == '__main__':
    from client import LogicBlockCraftTableDoubleClient


class LogicBlockCraftTableServer(LogicBlockServerBase):
    """
    合成台逻辑方块服务端\n
    - 方块数据独立
    - 仅提供数据处理功能
    """
    __mVersion__ = 2
    # 方块数据属性配置
    _data_config = {
        "storage_key": "",  # 数据键
        "syn_data_key": ""  # 同步数据键 - 客户端缓存
    }
    # 方块绑定玩家界面 默认在摧毁方块时关闭所有交互玩家的该界面
    _block_bind_ui = ""
    # 常加载方块：False时只在有交互玩家时才加载
    _const_block = False

    def __init__(self, name, dim, pos):
        super(LogicBlockCraftTableServer, self).__init__(name, dim, pos)
        self.craft_gen = None  # 合成生成器
        self.craft_tick = 30  # 制作cd
        self.state_crafting = False  # 正在制作

        # 注册方块摧毁回调 - 方块摧毁会掉落存储的物品
        self.RegisterBlockDestroyRecall()

    # -----------------------------------------------------------------------------------

    def CheckItemRecipe(self):
        # type: () -> bool
        """
        检测物品合成配方\n
        - 根据方块的缓存数据判断
        """

    # -----------------------------------------------------------------------------------

    def OnBlockDestroy(self):
        if self.craft_gen:
            self.StopCoroutine(self.craft_gen)
        # 反注册方块摧毁回调
        self.UnRegisterBlockDestroyRecall()
        # 清除方块数据 - 世界数据不会自动清除
        self.storage.clear()
        super(LogicBlockCraftTableServer, self).OnBlockDestroy()

    def OnPlayerDragSlot(self, player_id, src, des):
        # type: (str, str, str) -> None
        """
        玩家拖拽槽位\n
        - 方块数据槽位设计成 block<n>
        - 玩家数据槽位设计成 slot<n>
        - player_id: str
        - src: str
        - des: str
        """
        if self.state_crafting:
            print "[warn]", "正在合成物品：禁止操作"
            return
        self.UpdateBlockData(player_id, src, des)

    def OnActiveCraftItem(self):
        """激活合成物品"""

    def OnFinishedCraftItem(self):
        """结束合成物品"""

    # -----------------------------------------------------------------------------------

    def TryCraftItem(self):
        """尝试制作物品"""
        if self.state_crafting or not self.CheckItemRecipe():
            return

        def active():
            self.state_crafting = True
            self.OnActiveCraftItem()  # 激活合成
            yield self.craft_tick  # 合成等待时间
            self.OnFinishedCraftItem()  # 结束合成
            self.SaveBlockData()  # 保存数据
            self.state_crafting = False

        def reset():
            self.craft_gen = None
            if not self._player_set:
                self.ShuntDownBlock()

        self.craft_gen = self.StartCoroutine(active, reset)

    # -----------------------------------------------------------------------------------

    """方块数据相关"""

    def UpdateBlockData(self, player_id, src, des):
        # type: (str, str, str) -> bool
        """更新数据操作"""
        player = self.PlayerEntity(player_id)
        inventory = player.GetInventory()

        syn_data = False  # 修改了方块数据需要同步数据
        block_src = False  # 方块源数据

        # 源数据：方块数据
        if "block" in src:
            syn_data = True
            block_src = True
            src_item = getattr(self, src)  # type: dict
        # 源数据：玩家数据
        else:
            src_item = inventory.GetItemBySlotKey(src)  # type: dict

        if not src_item:
            print "[warn]", "源槽位无数据：", src
            return False

        # 目标数据：方块数据
        if "block" in des:
            syn_data = True
            des_item = getattr(self, des)
            if not block_src:
                # 玩家数据与方块数据交换
                setattr(self, des, src_item)
                inventory.SetItemBySlotKey(src, des_item)
            else:
                # 方块数据交换
                temp_des = copy.deepcopy(des_item)
                setattr(self, des, src_item)
                setattr(self, src, temp_des)
        # 目标数据：玩家数据
        else:
            des_item = inventory.GetItemBySlotKey(des)
            if block_src:
                # 方块数据到玩家数据
                setattr(self, src, des_item)
                inventory.SetItemBySlotKey(des, src_item)
            else:
                # 玩家数据到玩家数据 - 无需同步到其他客户端
                if not inventory.SetMergeBySlotKey(src, des):
                    inventory.SetExchangeBySlotKey(src, des)

        return syn_data

    def SaveBlockData(self):
        """服务端保存方块数据"""
        self.PackData()
        self.SaveData()

    def GetBlockData(self):
        # type: () -> dict
        """
        获得方块数据缓存\n
        - 用于客户端界面渲染显示和逻辑
        """

    def SynData(self):
        """
        客户端界面同步数据\n
        - 只需同步正在与玩家交互的玩家
        """
        super(LogicBlockCraftTableServer, self).SynData()

    # -----------------------------------------------------------------------------------

    """玩家相关"""

    def DelPlayer(self, player_id):
        self._player_set.discard(player_id)
        if not self._player_set and not self.state_crafting:
            # 非常加载方块无交互玩家则关闭实例
            self.ShuntDownBlock()


class LogicBlockCraftTableDoubleServer(LogicBlockCraftTableServer):
    """
    合成台逻辑方块双端服务端\n
    - 启用rpc
    - 方块数据公用
    - 需要定义方块数据
    """
    __mVersion__ = 2

    def __init__(self, name, dim, pos):
        super(LogicBlockCraftTableDoubleServer, self).__init__(name, dim, pos)
        self.rpc_key = Misc.CreateUUID()
        self.rpc = self.ModuleSystem.CreateRpcModule(self, self.rpc_key)
        self.dirty_player = set()

    # -----------------------------------------------------------------------------------

    def client(self, target=None):
        # type: (str) -> LogicBlockCraftTableDoubleClient
        return self.rpc(target)

    # -----------------------------------------------------------------------------------

    def OnDestroy(self):
        self.rpc.Discard()
        del self.rpc
        super(LogicBlockCraftTableDoubleServer, self).OnDestroy()

    def OnFinishedLoadData(self):
        super(LogicBlockCraftTableDoubleServer, self).OnFinishedLoadData()
        for player_id in list(self.dirty_player):
            self.AddPlayer(player_id)
        self.dirty_player.clear()

    # -----------------------------------------------------------------------------------

    """玩家相关"""

    def AddPlayer(self, player_id):
        if not self.flag_finished_load:
            self.dirty_player.add(player_id)
            return
        super(LogicBlockCraftTableDoubleServer, self).AddPlayer(player_id)
        self.NotifyToClient(player_id, ModuleEvent.ModuleOnBlockAddPlayerEvent, {
            "id": self.id,
            "rpc": self.rpc_key,
            "data": self.GetBlockData()
        })
