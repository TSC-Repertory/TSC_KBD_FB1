# -*- coding:utf-8 -*-


from const import *
from ..mdk.module.system.base import *
import random
from mod.common.utils.mcmath import Vector3
import math


class BaseModuleClient(ModuleClientBase):
    """base模块客户端"""
    __mVersion__ = 1
    __identifier__ = ModuleEnum.identifier

    def ConfigEvent(self):
        super(BaseModuleClient, self).ConfigEvent()
        self.defaultEvent.update({
            ClientEvent.AddEntityClientEvent: self.AddEntityClientEvent,
            ClientEvent.OnScriptTickClient: self._OnScriptTickClient,
        })
        self.serverEvent.update({
            "OnePlayEffect": self.OnePlayEffect,
            "Play_Mineraft_Particle": self.Play_Mineraft_Particle

        })
        self.comp_factory.CreateModAttr(self.local_id).RegisterUpdateFunc("tsc_kbd_attr_san", self.FB1_SanChange)

    # 生物出生播放特效
    def AddEntityClientEvent(self, args):
        entityId = args["id"]
        engineTypeStr = args["engineTypeStr"]
        pos = (args["posX"], args["posY"]+1, args["posZ"])
        if engineTypeStr in modConfig.MobEffectDict:
            effectDict = modConfig.MobEffectDict[engineTypeStr]
            for effect in effectDict.keys():

                particleEntityId0 = self.system.CreateEngineParticle(effect, pos)
                particleControlComp = self.comp_factory.CreateParticleControl(particleEntityId0)
                particleControlComp.Play()
                self.comp_factory.CreateParticleEntityBind(particleEntityId0).Bind(entityId, effectDict[effect], (0, 0, 0))

    def Play_Mineraft_Particle(self, args):
        effect_pos = args["pos"]
        effect_name = args["name"]
        dim = args["dim"]
        if dim != self.game_comp.GetCurrentDimension():
            return
        self.comp_factory.CreateParticleSystem(clientApi.GetLevelId()).Create(effect_name, effect_pos, (0, 1, 0))

    def OnePlayEffect(self, args):
        path = args["path"]
        entityId = args["entityId"]
        pos = args["pos"]
        bind = args.get("bind", None)
        delay = args.get("delay", 0)
        offset = args.get("offset", (0, 0, 0))
        particleEntityId0 = self.system.CreateEngineParticle(path, pos)
        particleControlComp = self.comp_factory.CreateParticleControl(particleEntityId0)
        particleControlComp.Play()
        if bind:
            self.comp_factory.CreateParticleEntityBind(particleEntityId0).Bind(entityId, offset, (0, 1, 0))

        self.add_timer(delay, self.system.DestroyEntity, particleEntityId0)

    def FB1_SanChange(self, args):
        newValue = args.get("newValue", 0)
        oldValue = args.get("oldValue", 0)
        max_value = 160.0
        rate = newValue / max_value
        if rate <= 0.4 and self.local_id not in self.spawn_cd:
            self.spawn_cd[self.local_id] = 30 * 60
            self.NotifyToServer("San_By_SpawnMob", {"playerId": self.local_id})

        if rate >= 0.7 and self.local_id in self.spawn_cd:
            self.NotifyToServer("San_By_DelMob", {"playerId": self.local_id})

    fb1_tick = 0
    spawn_cd = {}
    def _OnScriptTickClient(self):
        self.fb1_tick += 1
        if self.local_id in self.spawn_cd:
            self.spawn_cd[self.local_id] -= 1
            if self.spawn_cd[self.local_id] <= 0:
                self.spawn_cd.pop(self.local_id)

        if self.fb1_tick % 30 == 0:
            pass


