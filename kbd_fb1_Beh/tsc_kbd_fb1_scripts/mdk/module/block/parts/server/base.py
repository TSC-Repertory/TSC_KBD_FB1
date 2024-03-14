# -*- coding:utf-8 -*-


import weakref

from ..base import LogicBlockBase
from ...const import ModuleEvent
from .....common.utils.misc import Misc
from .....loader import MDKConfig
from .....server.system.base import ServerBaseSystem


class LogicBlockServerBase(ServerBaseSystem, LogicBlockBase):
    """逻辑方块服务端基类"""
    __mVersion__ = 6
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
        ServerBaseSystem.__init__(self, MDKConfig.GetModuleServer())
        LogicBlockBase.__init__(self, name, dim, pos)
        self._player_set = set()  # 交互玩家

    # -----------------------------------------------------------------------------------

    _block_module = None

    @property
    def BlockModule(self):
        # type: () -> MDKConfig.GetPresetModule().BlockModuleServer
        if LogicBlockServerBase._block_module:
            return LogicBlockServerBase._block_module
        module = self.ModuleSystem.GetModule("block")
        if not module:
            return None
        LogicBlockServerBase._block_module = weakref.proxy(module)
        return LogicBlockServerBase._block_module

    # -----------------------------------------------------------------------------------

    def RegisterBlockDestroyRecall(self):
        """
        注册方块销毁回调\n
        - 回调至方法<OnBlockDestroy>
        """
        self.BlockModule.RegisterBlockDestroyRecall(self._block_name, self.id)

    def UnRegisterBlockDestroyRecall(self):
        """反注册方块摧毁回调"""
        self.BlockModule.UnRegisterBlockDestroyRecall(self.block_name, self.id)

    # -----------------------------------------------------------------------------------

    def OnBlockDestroy(self):
        """
        方块被摧毁时触发\n
        - 仅由管理类调用
        """
        if self._block_bind_ui:
            player_list = list(self._player_set)
            self.NotifyToMultiClients(player_list, ModuleEvent.ModuleRequestShuntDownBlockEvent, {
                "blockId": self.id
            })
        self.ShuntDownBlock()

    # -----------------------------------------------------------------------------------

    def ShuntDownBlock(self):
        """请求管理关闭实例"""
        self.SaveData()
        self.BlockModule.DelLogicBlock(self.id)

    def SpawnItemAtBlock(self, item, offset=None):
        # type: (dict, tuple) -> None
        """生成物品到方块位置"""
        if offset:
            pos = Misc.GetPosModify(self._block_pos, offset)
            self.Item.SpawnAtPos(item, pos, self._block_dim)
        else:
            self.Item.SpawnAtPos(item, self._block_pos, self._block_dim)

    def SpawnItemListAtBlock(self, items, offset=None):
        # type: (any, tuple) -> None
        """生物物品列表到方块位置"""
        pos = self._block_pos if not offset else Misc.GetPosModify(self._block_pos, offset)
        dim = self._block_dim
        for item in items:
            if not item:
                continue
            self.Item.SpawnAtPos(item, pos, dim)

    # -----------------------------------------------------------------------------------

    """玩家操作"""

    def HasPlayer(self, player_id):
        # type: (str) -> bool
        """玩家是否正在交互"""
        return player_id in self._player_set

    def GetPlayer(self):
        return list(self._player_set)

    def AddPlayer(self, player_id):
        # type: (str) -> None
        """添加正在交互的玩家"""
        self._player_set.add(player_id)

    def DelPlayer(self, player_id):
        # type: (str) -> None
        """删除正在交互的玩家"""
        self._player_set.discard(player_id)
        if not self._player_set and not self._const_block:
            # 非常加载方块无交互玩家则关闭实例
            self.ShuntDownBlock()

    """数据操作"""

    def GetData(self, key):
        storage = self.GetLevelStorage(key)
        return storage.get(self.id, {})

    def SetData(self, key, value):
        storage = self.GetLevelStorage(key)
        storage[self.id] = value
        self.SetLevelStorage(key, storage)

    def ClearData(self):
        key = self._data_config["storage_key"]
        storage = self.GetData(key)
        storage.pop(self.id, None)
        if not storage:
            self.ClearLevelStorage(key)
        else:
            self.SetLevelStorage(key, storage)
