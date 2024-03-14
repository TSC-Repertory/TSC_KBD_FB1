# -*- coding:utf-8 -*-


from const import *
from ..system.base import *


class MobModuleClient(ModuleClientBase):
    """生物模块客户端"""
    __mVersion__ = 3
    __identifier__ = ModuleEnum.identifier

    def __init__(self):
        super(MobModuleClient, self).__init__()
        self._player_class_map = set()
        self._player_storage = {}

    def OnDestroy(self):
        del self._player_class_map
        for player_ins in self._player_storage.values():
            player_ins.OnDestroy()
        del self._player_storage
        super(MobModuleClient, self).OnDestroy()

    def ConfigEvent(self):
        super(MobModuleClient, self).ConfigEvent()
        self.clientEvent.update({
            ClientEvent.ClientModuleFinishedLoadEvent: self.ClientModuleFinishedLoadEvent
        })

    def RegisterPlayerClass(self, player_class):
        """添加玩家类"""
        self._player_class_map.add(player_class)

    # -----------------------------------------------------------------------------------

    def ClientModuleFinishedLoadEvent(self, _):
        pack = {"add": self.RegisterPlayerClass}
        self.BroadcastEvent(ModuleEvent.ModuleRequestPlayerClassMapEvent, pack)
        if not self._player_class_map:
            print "[warn]", "empty player class map! destroying mob module client."
            self.ModuleSystem.DelModule(ModuleEnum.identifier)
        else:
            for player_class in self._player_class_map:
                player_ins = player_class()
                self._player_storage[id(player_ins)] = player_ins
