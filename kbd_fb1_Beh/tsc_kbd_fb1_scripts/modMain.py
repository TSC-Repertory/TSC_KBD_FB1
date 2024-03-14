# -*- coding: utf-8 -*-


from mod.common.mod import Mod

from mdk.loader import *
from mdk.module import preset_module
from base import *


@Mod.Binding("tsc_kbd_fb1", "1.0.0")
class TestMod(object):

    @Mod.InitServer()
    def ServerInit(self):
        system = MDKConfig.InitModuleServer()
        register = system.GetRegister()
        # -----------------------------------------------------------------------------------
        register.RegisterModule(preset_module.MobModuleServer)
        register.RegisterModule(preset_module.ParticleModuleServer)
        # -----------------------------------------------------------------------------------
        register.RegisterModule(BaseModuleServer)

    @Mod.InitClient()
    def ClientInit(self):
        system = MDKConfig.InitModuleClient()
        register = system.GetRegister()
        # -----------------------------------------------------------------------------------
        register.RegisterModule(preset_module.MobModuleClient)
        register.RegisterModule(preset_module.ParticleModuleClient)
        register.RegisterModule(preset_module.MusicModuleClient)
        # -----------------------------------------------------------------------------------
        register.RegisterModule(BaseModuleClient)
