# -*- coding:utf-8 -*-



class StorageBase(object):
    """数据基类"""
    __mVersion__ = 4

    def HasData(self, *args, **kwargs):
        """判断是否存在数据"""

    def AddData(self, *args, **kwargs):
        """添加数据"""

    def DelData(self, *args, **kwargs):
        """删除数据"""

    def ClearData(self, *args, **kwargs):
        """清除数据"""

    def GetData(self, *args, **kwargs):
        """获得数据"""

    def SetData(self, *args, **kwargs):
        """设置数据"""

    def InitData(self, *args, **kwargs):
        """初始化数据"""

    def SaveData(self, *args, **kwargs):
        """存储数据"""

    def LoadData(self, *args, **kwargs):
        """读取数据"""

    def ReloadData(self, *args, **kwargs):
        """重载数据"""

    def PackData(self, *args, **kwargs):
        """封装数据"""

    def SynData(self, *args, **kwargs):
        """同步数据"""

    def RegisterData(self, *args, **kwargs):
        """注册数据"""

    def UnRegisterData(self, *args, **kwargs):
        """反注册数据"""


class StoragePreset(StorageBase):
    """
    数据预设类\n
    - 需要实现：GetData SetData
    """
    __mVersion__ = 2
    _data_config = {
        "storage_key": "",  # 数据键
        "syn_data_key": ""  # 同步数据键 - 客户端缓存
    }

    def __init__(self):
        super(StoragePreset, self).__init__()
        # 注册属性数据
        self._register_storage_data = {}
        # 属性存储字典
        self.storage = {}
        # 完成加载标志
        self.flag_finished_load = False
        # 同步标志
        self.flag_syn_data = False
        # 开启注册数据
        self.ConfigRegisterData()

    def ConfigRegisterData(self):
        """配置注册数据"""

    # -----------------------------------------------------------------------------------

    def IsFinishedLoad(self):
        # type: () -> bool
        """是否完成加载"""
        return self.flag_finished_load

    # -----------------------------------------------------------------------------------

    def OnFinishedReloadStorage(self):
        """
        完成数据重载回调\n
        - 用于修正新版本数据兼容问题
        """

    def OnFinishedLoadData(self):
        """完成数据导入回调"""
        self.SynData()

    # -----------------------------------------------------------------------------------

    """数据相关"""

    def RegisterData(self, key, default=0, bind=None):
        # type: (str, any, str) -> None
        if not bind:
            bind = key
        self._register_storage_data[key] = (bind, default)

    def UnRegisterData(self, key):
        # type: (str) -> None
        self._register_storage_data.pop(key, None)
        self.storage.pop(key, None)

    def PackData(self):
        for key, config in self._register_storage_data.iteritems():
            self.storage[key] = getattr(self, config[0])

    def InitData(self):
        for config in self._register_storage_data.itervalues():
            setattr(self, *config)

    def ReloadData(self, storage):
        # type: (dict) -> None
        load_key = set()
        for key, value in storage.iteritems():
            if hasattr(self, key):
                setattr(self, key, value)
                load_key.add(key)
        # 检测新数据键 使用默认值
        register_key = set(self._register_storage_data.keys())
        for key in register_key.difference(load_key):
            setattr(self, *self._register_storage_data[key])
        self.PackData()

    def LoadData(self):
        """
        导入数据\n
        - 调用时刻：客户端模组加载完成时
        """
        self.InitData()
        storage = self.GetData(self._data_config["storage_key"])
        if not storage:
            self.PackData()
            self.SaveData(False)
        else:
            self.ReloadData(storage)
            self.OnFinishedReloadStorage()
        self.flag_finished_load = True
        self.OnFinishedLoadData()

    def GetData(self, key):
        # type: (str) -> dict
        """获取数据"""

    def SetData(self, key, value):
        # type: (str, dict) -> None
        """设置数据"""

    def SaveData(self, syn_data=True):
        self.SetData(self._data_config["storage_key"], self.storage)
        if syn_data:
            self.SynData()

    def SynData(self):
        self.flag_syn_data = False
