# -*- coding:utf-8 -*-


from const import *
from ...module.system.base import *


class MusicModuleClient(ModuleClientBase):
    """音乐模块客户端"""
    __mVersion__ = 3
    __identifier__ = ModuleEnum.identifier

    def ConfigEvent(self):
        super(MusicModuleClient, self).ConfigEvent()
        self.serverEvent.update({
            ServerEvent.RequestPlayMusicEvent: self.RequestPlayMusicEvent,
            "StopMusic": self.StopMusic,
        })

    musicId = {}
    def RequestPlayMusicEvent(self, args):
        entityId = args.get("entityId")
        name = args["name"]
        stop = args.get("stop", 0)
        loop = args.get("loop", False)
        self.musicId[entityId] = self.PlayMusic(entityId, name, stop=stop, loop=loop)

    def StopMusic(self, args):
        entityId = args.get("entityId")
        if self.musicId and entityId in self.musicId:
            self.comp_factory.CreateCustomAudio(clientApi.GetLevelId()).StopCustomMusicById(self.musicId[entityId], 0)
            self.musicId.pop(entityId)
