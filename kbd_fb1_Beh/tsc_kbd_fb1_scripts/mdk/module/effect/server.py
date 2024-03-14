# -*- coding:utf-8 -*-


import re

from const import *
from parts.base import ModuleEffectBase
from ..system.base import *
from ...server.entity import RawEntity


class EffectModuleServer(ModuleServerBase):
    """效果模块服务端"""
    __mVersion__ = 9
    __identifier__ = ModuleEnum.identifier

    def __init__(self):
        super(EffectModuleServer, self).__init__()
        self._effect_map = {}  # effect_name: [effect_class]
        self._effect_storage = {}  # effect_name: {entity_id: {uid: effect_ins}}
        self._entity_effect = {}  # entity_id: {effect_name}

    def OnDestroy(self):
        # 退出时生物模块已调用效果实例销毁方块
        del self._effect_map
        del self._effect_storage
        del self._entity_effect
        super(EffectModuleServer, self).OnDestroy()

    def ConfigEvent(self):
        super(EffectModuleServer, self).ConfigEvent()
        self.defaultEvent.update({
            ServerEvent.ClientLoadAddonsFinishServerEvent: self.ClientLoadAddonsFinishServerEvent,
            ServerEvent.AddEffectServerEvent: self.AddEffectServerEvent,
            ServerEvent.RefreshEffectServerEvent: self.RefreshEffectServerEvent,
            ServerEvent.RemoveEffectServerEvent: self.RemoveEffectServerEvent,
            ServerEvent.WillAddEffectServerEvent: self.WillAddEffectServerEvent,
            ServerEvent.CommandEvent: self.CommandEvent,
        })
        self.serverEvent.update({
            ServerEvent.ServerModuleFinishedLoadEvent: self.ServerModuleFinishedLoadEvent,
        })

    # -----------------------------------------------------------------------------------

    _mob_module = None

    @property
    def MobModule(self):
        # type: () -> MDKConfig.GetPresetModule().MobModuleServer
        if EffectModuleServer._mob_module:
            return EffectModuleServer._mob_module
        module = self.ModuleSystem.GetModule("mob")
        if not module:
            return None
        EffectModuleServer._mob_module = weakref.proxy(module)
        return EffectModuleServer._mob_module

    # -----------------------------------------------------------------------------------

    def RegisterEffectClass(self, effect_class):
        # type: (ModuleEffectBase) -> None
        """添加效果类"""
        effect_name = effect_class.GetEffectName()
        if effect_name not in self._effect_map:
            self._effect_map[effect_name] = set()
        class_set = self._effect_map[effect_name]  # type: set
        class_set.add(effect_class)

    def DestroyEntityEffect(self, entity_id, effect_name, effect_id):
        # type: (str, str, str) -> None
        """销毁实体指定效果实例"""
        effect_storage = self._effect_storage.get(effect_name)  # type: dict
        if not effect_storage:
            return

        entity_storage = effect_storage.get(entity_id)  # type: dict
        if not entity_storage:
            print "[error]", "[DestroyEntityEffect]", "empty entity effect storage: %s" % effect_name
            return

        effect_ins = entity_storage.pop(effect_id, None)  # type: ModuleEffectBase
        if effect_ins.OnDestroy():  # 清除生物模块引用
            self.MobModule.DelMobIns(entity_id, id(effect_ins))

        if entity_storage:
            return
        effect_storage.pop(entity_id, None)
        if not effect_storage:
            self._effect_storage.pop(effect_name, None)

        # 实体效果缓存
        effect_cache = self._entity_effect.get(entity_id, set())
        effect_cache.discard(effect_name)
        if not effect_cache:
            self._entity_effect.pop(entity_id, None)

    def DestroyEntityAllEffect(self, entity_id):
        # type: (str) -> None
        """销毁实体的全部效果实例"""
        if entity_id not in self._entity_effect:
            return
        for effect_name in self._entity_effect[entity_id]:
            effect_storage = self._effect_storage[effect_name]  # type: dict
            entity_storage = effect_storage[entity_id]  # type: dict
            for effect_id, effect_ins in entity_storage.items():
                if effect_ins.OnDestroy():  # 清除生物模块引用
                    self.MobModule.DelMobIns(entity_id, id(effect_ins))
            effect_storage.pop(entity_id, None)
            if not effect_storage:
                self._effect_storage.pop(effect_name, None)
        self._entity_effect.pop(entity_id, None)

    # -----------------------------------------------------------------------------------

    """效果相关"""

    def AddEffectServerEvent(self, args):
        entity_id = args["entityId"]
        effect_name = args["effectName"]
        if effect_name not in self._effect_map:
            return
        effect_set = self._effect_map[effect_name]

        # 实体效果缓存
        if entity_id not in self._entity_effect:
            self._entity_effect[entity_id] = set()
        effect_cache = self._entity_effect[entity_id]  # type: set
        effect_cache.add(effect_name)

        if effect_name not in self._effect_storage:
            self._effect_storage[effect_name] = {}
        effect_storage = self._effect_storage[effect_name]  # type: dict

        if entity_id not in effect_storage:
            effect_storage[entity_id] = {}
        entity_storage = effect_storage[entity_id]  # type: dict

        for effect_class in list(effect_set):
            effect_ins = effect_class(entity_id)
            entity_storage[id(effect_ins)] = effect_ins
            # todo: 生物区块卸载将丢失全部效果
            self.MobModule.AddMobIns(entity_id, effect_ins)

    def RemoveEffectServerEvent(self, args):
        entity_id = args["entityId"]
        effect_name = args["effectName"]
        if effect_name not in self._effect_map:
            return

        duration = args["effectDuration"]
        level = args["effectAmplifier"]
        effect_storage = self._effect_storage[effect_name]  # type: dict
        entity_storage = effect_storage.pop(entity_id, None)  # type: dict
        if not effect_storage:
            self._effect_storage.pop(effect_name, None)

        # 实体效果缓存
        effect_cache = self._entity_effect.get(entity_id, set())
        effect_cache.discard(effect_name)
        if not effect_cache:
            self._entity_effect.pop(entity_id, None)

        if not entity_storage:
            print "[warn]", "[RemoveEffectServerEvent]", "empty entity effect storage: %s" % effect_name
            return

        for effect_ins in entity_storage.values():
            assert isinstance(effect_ins, ModuleEffectBase)
            effect_ins.OnRemoveEffect(duration, level)
            if effect_ins.OnDestroy():  # 清除生物模块引用
                self.MobModule.DelMobIns(entity_id, id(effect_ins))
        entity_storage.clear()

    def RefreshEffectServerEvent(self, args):
        entity_id = args["entityId"]
        effect_name = args["effectName"]
        if effect_name not in self._effect_map:
            return

        duration = args["effectDuration"]
        level = args["effectAmplifier"]
        effect_storage = self._effect_storage[effect_name]  # type: dict
        entity_storage = effect_storage.get(entity_id)  # type: dict
        if not entity_storage:
            print "[warn]", "[RefreshEffectServerEvent]", "empty entity effect storage: %s" % effect_name
            return

        for effect_ins in entity_storage.values():
            effect_ins.OnRefreshEffect(duration, level)

    def WillAddEffectServerEvent(self, args):
        entity_id = args["entityId"]
        effect_name = args["effectName"]
        if effect_name not in self._effect_map:
            return

        duration = args["effectDuration"]
        level = args["effectAmplifier"]
        effect_storage = self._effect_storage.get(effect_name)  # type: dict
        if not effect_storage:
            return
        entity_storage = effect_storage.get(entity_id)  # type: dict
        if not entity_storage:
            return

        for effect_ins in entity_storage.values():
            add = effect_ins.OnWillAddEffect(duration, level)
            if not add:
                args["cancel"] = True
                return

    def ServerModuleFinishedLoadEvent(self, _):
        def active():
            if not self._effect_map:
                print "[warn]", "empty effect class map! destroying effect module."
                self.ModuleSystem.DelModule(ModuleEnum.identifier)

        self.DelayTickFunc(30, active)

    # -----------------------------------------------------------------------------------

    def CommandEvent(self, args):
        player_id = args["entityId"]
        command = args["command"]  # type: str
        if command.startswith("/effect "):
            effect_list = re.findall(r"/effect (.*?) (\d+) (\d+)", command)[0]
            effect_list = [effect_list[0]] + [int(param) for param in effect_list[1:]]
            if RawEntity.AddEffect(player_id, *effect_list):
                args["cancel"] = True
