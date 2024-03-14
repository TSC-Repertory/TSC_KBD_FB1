# -*- coding:utf-8 -*-


from ...system.preset import *
from ....interface.data.base import StoragePreset


class ItemModuleServerBase(LoadConfigModuleServer, StoragePreset):
    """
    物品模块服务端基类\n
    - 读取配置文件
    - 数据保存
    """
    __mVersion__ = 2

    def __init__(self):
        super(ItemModuleServerBase, self).__init__()
        LoadConfigModuleServer.__init__(self)
        StoragePreset.__init__(self)

    def SetData(self, key, value):
        self.SetLevelStorage(self._data_config["storage_key"], self.storage)

    def GetData(self, key):
        return self.GetLevelStorage(self._data_config["storage_key"])

    def OnFinishedLoadData(self):
        self.ModuleSystem.RegisterUpdateSecond(self.OnUpdateSecond)

    def OnUpdateSecond(self):
        """秒更新"""
