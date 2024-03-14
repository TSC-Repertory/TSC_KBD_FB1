# -*- coding:utf-8 -*-


from ....interface.data.base import StoragePreset


class LogicBlockBase(StoragePreset):
    """逻辑方块基类"""
    __mVersion__ = 1
    # 方块绑定玩家界面
    _block_bind_ui = ""
    # 方块数据属性配置
    _data_config = {
        "storage_key": "",  # 数据键
        "syn_data_key": ""  # 同步数据键 - 客户端缓存
    }

    def __init__(self, name, dim, pos):
        super(LogicBlockBase, self).__init__()
        self._block_name = name
        self._block_dim = dim
        self._block_pos = pos

    # -----------------------------------------------------------------------------------

    @property
    def id(self):
        # type: () -> tuple
        """获得代表该实例的标识"""
        return self._block_name, self._block_dim, self._block_pos

    @property
    def block_name(self):
        # type: () -> str
        """方块名称"""
        return self._block_name

    @property
    def block_dim(self):
        # type: () -> int
        """方块维度"""
        return self._block_dim

    @property
    def block_pos(self):
        # type: () -> tuple
        """方块位置"""
        return self._block_pos

    # -----------------------------------------------------------------------------------

    def OnUpdateTick(self):
        """
        Tick更新\n
        - 仅由管理类调用
        """

    def OnUpdateSecond(self):
        """
        秒更新\n
        - 仅由管理类调用
        """

    # -----------------------------------------------------------------------------------

    def GetBindUI(self):
        # type: () -> str
        """获得逻辑方块绑定的界面键"""
        return self._block_bind_ui

    # -----------------------------------------------------------------------------------

    def ShuntDownBlock(self):
        """请求管理关闭实例"""
