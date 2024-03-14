# -*- coding:utf-8 -*-


from const import *
from parser import TagParser
from ...module.system.base import *


class TagModuleClient(ModuleClientBase):
    """标签模块客户端"""
    __mVersion__ = 2
    __identifier__ = ModuleEnum.identifier

    def __init__(self):
        super(TagModuleClient, self).__init__()
        self.ModuleSystem.SetModConfigParser(TagParser())

    def ConfigEvent(self):
        super(TagModuleClient, self).ConfigEvent()
        self.serverEvent.update({
            ModuleEvent.ModuleRequestSynTagDataEvent: self.ModuleRequestSynTagDataEvent
        })

        # -----------------------------------------------------------------------------------

    @classmethod
    def ModuleRequestSynTagDataEvent(cls, args):
        data = args["data"]
        ModuleTag.TagStorage = data
