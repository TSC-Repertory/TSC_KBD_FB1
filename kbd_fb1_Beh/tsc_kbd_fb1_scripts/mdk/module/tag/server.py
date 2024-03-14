# -*- coding:utf-8 -*-


from const import *
from ...module.system.preset import *


class TagModuleServer(LoadConfigModuleServer):
    """标签模块服务端"""
    __mVersion__ = 1
    __identifier__ = ModuleEnum.identifier
    _ModuleRequestRegisterEvent = ModuleEvent.ModuleRequestTagRegisterEvent

    def __init__(self):
        super(TagModuleServer, self).__init__()
        self._dirty_player = set()

    # -----------------------------------------------------------------------------------

    def GetDefaultConfig(self):  # type: () -> list
        return ["tags/root.json"]

    def OnLoadModConfig(self, data):
        ModuleTag.TagStorage = data
        recall = self.defaultEvent.pop(ServerEvent.ClientLoadAddonsFinishServerEvent)
        self.UnListenBaseServer(ServerEvent.ClientLoadAddonsFinishServerEvent, recall)

        for playerId in self._dirty_player:
            self.NotifyToClient(playerId, ModuleEvent.ModuleRequestSynTagDataEvent, {
                "data": data
            })
        self._dirty_player.clear()
        return True

    # -----------------------------------------------------------------------------------

    def ClientLoadAddonsFinishServerEvent(self, args):
        playerId = args["playerId"]
        if not self._load_data:
            self._dirty_player.add(playerId)
            return
        self.NotifyToClient(playerId, ModuleEvent.ModuleRequestSynTagDataEvent, {
            "data": ModuleTag.TagStorage
        })
