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
            "San_By_SpawnMob": self.San_By_SpawnMob,
            "San_By_DelMob": self.San_By_DelMob
        })

        self.serverEvent.update({
            ServerEvent.ServerModuleFinishedLoadEvent: self.ServerModuleFinishedLoadEvent
        })
        self.defaultEvent.update({
            ServerEvent.PlayerDieEvent: self.PlayerDieEvent
        })

    def ServerModuleFinishedLoadEvent(self, _):
        module_id = preset_module.MobModuleServer.GetId()
        module = self.ModuleSystem.GetModule(module_id)  # type: preset_module.MobModuleServer

        # 生物注册
        module.RegisterMobClass("tsc:mlzzz", MLZZZEntity)
        module.RegisterMobClass("tsc:qxdkj", QXDKJEntity)
        module.RegisterMobClass("tsc:wyqxz", WYQXZEntity)
        module.RegisterMobClass("tsc:jegzz", JZGZZEntity)

    def San_By_SpawnMob(self, args):
        playerId = args["playerId"]
        pos = RawEntity.GetPos(playerId)
        dim = RawEntity.GetDim(playerId)
        s_pos = Misc.GetRandomPointFromRing(pos, 10, 15, 2)
        e_id = RawEntity.CreateRaw("tsc:mlzzz", s_pos[0], dim)
        e_id2 = RawEntity.CreateRaw("tsc:qxdkj", s_pos[1], dim)

        data_comp = self.comp_factory.CreateExtraData(playerId)
        tsc_san_spawn_mob_list = data_comp.GetExtraData("tsc_san_spawn_mob_list")
        if not tsc_san_spawn_mob_list:
            data_comp.SetExtraData("tsc_san_spawn_mob_list", [e_id, e_id2])
        else:
            tsc_san_spawn_mob_list.append(e_id)
            tsc_san_spawn_mob_list.append(e_id2)
            data_comp.SetExtraData("tsc_san_spawn_mob_list", tsc_san_spawn_mob_list)

    def PlayerDieEvent(self, args):
        playerId = args["id"]
        data_comp = self.comp_factory.CreateExtraData(playerId)
        tsc_san_spawn_mob_list = data_comp.GetExtraData("tsc_san_spawn_mob_list")
        if tsc_san_spawn_mob_list:
            for e_id in tsc_san_spawn_mob_list:
                self.system.DestroyEntity(e_id)

            data_comp.SetExtraData("tsc_san_spawn_mob_list", None)

    def San_By_DelMob(self, args):
        playerId = args["playerId"]
        data_comp = self.comp_factory.CreateExtraData(playerId)
        tsc_san_spawn_mob_list = data_comp.GetExtraData("tsc_san_spawn_mob_list")
        if tsc_san_spawn_mob_list:
            for e_id in tsc_san_spawn_mob_list:
                self.system.DestroyEntity(e_id)

            data_comp.SetExtraData("tsc_san_spawn_mob_list", None)
