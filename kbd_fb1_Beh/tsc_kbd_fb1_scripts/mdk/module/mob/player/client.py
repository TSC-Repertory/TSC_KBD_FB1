# -*- coding:utf-8 -*-


from ....client.system.base import ClientBaseSystem
from ....interface.data.base import StoragePreset
from ....loader import MDKConfig

"""
玩家模块基类 - 客户端
- 常用于复杂模组的玩家操作
- 使用本地储存数据

- global_data: bool 是否全局数据
"""


class ModulePlayerBase(ClientBaseSystem, StoragePreset):
    """模块玩家基类"""
    __mVersion__ = 7
    _data_config = {
        "storage_key": "",  # 数据键
    }

    def __init__(self, **kwargs):
        ClientBaseSystem.__init__(self, MDKConfig.GetModuleClient())
        StoragePreset.__init__(self)
        self.global_data = kwargs.get("global_data", False)  # 全局数据

    # -----------------------------------------------------------------------------------

    """数据相关"""

    def GetData(self, key):
        return self.GetLocalConfigData(key, self.global_data)

    def SetData(self, key, value):
        self.SetLocalConfigData(key, value, self.global_data)
