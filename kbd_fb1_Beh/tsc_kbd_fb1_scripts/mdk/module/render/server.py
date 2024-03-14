# -*- coding:utf-8 -*-


from const import *
from ..system.preset import *
from parser import RenderParser


class RenderModuleServer(LoadConfigModuleServer):
    """渲染模块服务端"""
    __mVersion__ = 4
    __identifier__ = ModuleEnum.identifier
    _ModuleRequestRegisterEvent = ModuleEvent.ModuleRequestRenderRegisterEvent
    _RegisterDataParser = RenderParser.GetId()

    def __init__(self):
        super(RenderModuleServer, self).__init__()
        self.dirty_player = set()

    def GetDefaultConfig(self):
        return ["render/root.json"]

    def ClientLoadAddonsFinishServerEvent(self, args):
        player_id = args["playerId"]
        if self._load_data:
            self.NotifyToClient(player_id, ModuleEvent.ModuleRequestSynRenderDataEvent, {
                "global": ModuleRender.GlobalRenderData,
                "player": ModuleRender.PlayerRenderData,
                "mob": ModuleRender.MobRenderData
            })
            return
        self.dirty_player.add(player_id)

    def OnLoadModConfig(self, data):
        if data:
            ModuleRender.GlobalRenderData = data["global"]
            ModuleRender.PlayerRenderData = data["player"]
            ModuleRender.MobRenderData = data["mob"]
            for player_id in list(self.dirty_player):
                self.NotifyToClient(player_id, ModuleEvent.ModuleRequestSynRenderDataEvent, {
                    "global": ModuleRender.GlobalRenderData,
                    "player": ModuleRender.PlayerRenderData,
                    "mob": ModuleRender.MobRenderData
                })
        self.dirty_player.clear()
        return True
