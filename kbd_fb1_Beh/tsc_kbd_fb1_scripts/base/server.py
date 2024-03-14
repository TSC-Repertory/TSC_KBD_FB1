# -*- coding:utf-8 -*-

import time

from const import *
from ..mdk.module import preset_module
from ..mdk.module.system.base import *
from ..mdk.server.entity import *
from ..mob.aggressive.kbd_fb1_mob import *


class BaseModuleServer(ModuleServerBase):
    """base模块服务端"""
    __mVersion__ = 1
    __identifier__ = ModuleEnum.identifier

    def ConfigEvent(self):
        super(BaseModuleServer, self).ConfigEvent()
        self.clientEvent.update({
        })

        self.serverEvent.update({
            ServerEvent.ServerModuleFinishedLoadEvent: self.ServerModuleFinishedLoadEvent
        })
        self.defaultEvent.update({
        })

    def ServerModuleFinishedLoadEvent(self, _):
        module_id = preset_module.MobModuleServer.GetId()
        module = self.ModuleSystem.GetModule(module_id)  # type: preset_module.MobModuleServer

        # 生物注册
        module.RegisterMobClass("zdkj:fog_man", FogManEntity)

