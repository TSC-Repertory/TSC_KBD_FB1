# -*- coding:utf-8 -*-


import weakref

from ..base import LogicBlockBase
from .....client.system.base import ClientBaseSystem
from .....loader import MDKConfig


class LogicBlockClientBase(ClientBaseSystem, LogicBlockBase):
    """
    逻辑方块客户端基类\n
    - 客户端的所有操作仅仅是缓存
    - 真实数据操作在服务端
    """
    __mVersion__ = 1
    # 方块绑定玩家界面 退出界面时关闭该实例
    _block_bind_ui = ""
    # 方块数据属性配置
    _data_config = {
        "storage_key": "",  # 数据键
        "syn_data_key": ""  # 同步数据键 - 客户端缓存
    }

    def __init__(self, name, dim, pos):
        ClientBaseSystem.__init__(self, MDKConfig.GetModuleServer())
        LogicBlockBase.__init__(self, name, dim, pos)

    # -----------------------------------------------------------------------------------

    _block_module = None

    @property
    def BlockModule(self):
        # type: () -> MDKConfig.GetPresetModule().BlockModuleClient
        if LogicBlockClientBase._block_module:
            return LogicBlockClientBase._block_module
        module = self.ModuleSystem.GetModule("block")
        if not module:
            return None
        LogicBlockClientBase._block_module = weakref.proxy(module)
        return LogicBlockClientBase._block_module

    # -----------------------------------------------------------------------------------

    def OnUISetExit(self):
        """
        退出界面时回调\n
        - 由界面调用
        """

    def OnUIFinishedCreate(self):
        """界面完成创建回调"""

    def OnServerRequestShuntDown(self):
        """
        服务端请求关闭界面\n
        - 由管理调用
        - 用于保存逻辑方块内容和关闭界面
        - 管理将自动删除方块实例
        """

    def OnServerBlockAddPlayer(self, rpc, data):
        # type: (str, dict) -> None
        """
        服务端方块添加玩家回传数据\n
        - 由管理调用
        """

    def OnServerSynData(self, data):
        # type: (dict) -> None
        """
        服务端数据同步数据\n
        - 由服务端rpc调用
        """

    # -----------------------------------------------------------------------------------

    def ShuntDownBlock(self):
        """请求管理关闭实例"""
        self.SaveData()
        self.BlockModule.DelLogicBlock(self.id)

    # -----------------------------------------------------------------------------------

    """数据操作"""

    def GetData(self, key, is_global=False):
        storage = self.GetLocalConfigData(key, is_global)
        return storage.get(key, {})

    def SetData(self, key, value, is_global=False):
        storage = self.GetLocalConfigData(key)
        storage[self.id] = value
        self.SetLocalConfigData(key, value, is_global)

    def ClearData(self, is_global=False):
        key = self._data_config["storage_key"]
        storage = self.GetData(key)
        storage.pop(self.id, None)
        self.SetLocalConfigData(key, storage, is_global)
