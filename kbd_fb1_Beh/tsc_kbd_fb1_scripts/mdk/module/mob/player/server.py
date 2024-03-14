# -*- coding:utf-8 -*-


import weakref

from ..parts.entity import ModuleEntityMgr
from ....common.system.event import ServerEvent
from ....interface.data.base import StoragePreset
from ....loader import MDKConfig
from ....server.entity.player_entity import PlayerEntity

"""
玩家模块基类 - 服务端
- 常用于复杂模组的玩家操作
- 使用ExtraData储存数据
"""


class ModulePlayerBase(PlayerEntity, StoragePreset):
    """
    模块玩家基类\n
    - 不具备系统功能 需要继承<ModuleEntityMgr>的超类
    """
    __mVersion__ = 5
    _data_config = {
        "storage_key": "",  # 数据键
        "syn_data_key": ""  # 同步数据键 - 客户端缓存
    }

    def __init__(self, playerId):
        PlayerEntity.__init__(self, playerId)
        StoragePreset.__init__(self)

    # -----------------------------------------------------------------------------------

    """数据相关"""

    def GetData(self, key):
        return self.GetStorage(key)

    def SetData(self, key, value):
        self.SetStorage(key, value)

    def SynData(self):
        super(ModulePlayerBase, self).SynData()
        self.PackData()
        self.NotifyToLocalClient(ServerEvent.RequestSynchronizeStorageEvent, {
            "key": self._data_config["syn_data_key"],
            "data": self.storage
        })


class ModulePlayerPreset(ModuleEntityMgr, ModulePlayerBase):
    """模块玩家预设"""
    __mVersion__ = 2

    def __init__(self, playerId):
        ModuleEntityMgr.__init__(self, MDKConfig.GetModuleServer())
        ModulePlayerBase.__init__(self, playerId)

    def OnDestroy(self):
        ModuleEntityMgr.OnDestroy(self)

    _mob_module = None

    @property
    def MobModule(self):
        # type: () -> MDKConfig.GetPresetModule().MobModuleServer
        if ModuleEntityMgr._mob_module:
            return ModuleEntityMgr._mob_module
        module = self.ModuleSystem.GetModule(MDKConfig.GetPresetModule().MobModuleServer.GetId())
        if not module:
            return None
        ModuleEntityMgr._mob_module = weakref.proxy(module)
        return ModuleEntityMgr._mob_module

    def RegisterHitRecall(self):
        """注册碰撞回调"""
        self.MobModule.RegisterHitDetection(self.id)

    def UnRegisterHitRecall(self):
        """反注册碰撞回调"""
        self.MobModule.UnRegisterHitDetection(self.id)
