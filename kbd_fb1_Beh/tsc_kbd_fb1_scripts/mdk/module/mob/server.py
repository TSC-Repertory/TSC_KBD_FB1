# -*- coding:utf-8 -*-


from const import *
from parts.entity import ModuleEntityPreset
from ..system.base import *
from ...server.entity.raw_entity import RawEntity


class MobModuleServer(ModuleServerBase):
    """生物模块服务端"""
    __mVersion__ = 10
    __identifier__ = ModuleEnum.identifier

    def __init__(self):
        super(MobModuleServer, self).__init__()
        self._second5 = 0
        self.flag_finished_load = False
        self.dirty_entity = set()

        self.mob_class_map = {}  # engineType: {entityClass}
        self.entity_storage = {}  # entity_id: EntityServerBase
        self.hit_recall = set()
        self.entity_getter = self.entity_storage.get

    def OnDestroy(self):
        del self.mob_class_map
        del self.entity_getter
        for entity_storage in self.entity_storage.values():
            for entity_ins in entity_storage.values():
                entity_ins.OnDestroy()
            entity_storage.clear()
        del self.entity_storage
        self.ModuleSystem.UnRegisterUpdateSecond(self.OnUpdateSecond)
        super(MobModuleServer, self).OnDestroy()

    def ConfigEvent(self):
        super(MobModuleServer, self).ConfigEvent()
        self.defaultEvent.update({
            ServerEvent.EntityRemoveEvent: self.EntityRemoveEvent,
            ServerEvent.AddEntityServerEvent: self.AddEntityServerEvent,
            ServerEvent.ChunkAcquireDiscardedServerEvent: self.ChunkAcquireDiscardedServerEvent,
            ServerEvent.ClientLoadAddonsFinishServerEvent: self.ClientLoadAddonsFinishServerEvent,
            ServerEvent.PlayerIntendLeaveServerEvent: self.PlayerIntendLeaveServerEvent,
            ServerEvent.HealthChangeBeforeServerEvent: self.HealthChangeBeforeServerEvent,
            ServerEvent.DamageEvent: (self.DamageEvent, 10),
            ServerEvent.MobDieEvent: (self.MobDieEvent, 10),
            ServerEvent.ActuallyHurtServerEvent: (self.ActuallyHurtServerEvent, 1),
            ServerEvent.EntityDefinitionsEventServerEvent: (self.EntityDefinitionsEventServerEvent, 10),
            ServerEvent.PlayerDoInteractServerEvent: (self.PlayerDoInteractServerEvent, 10),
            ServerEvent.OnMobHitMobServerEvent: self.OnMobHitMobServerEvent,
        })
        self.serverEvent.update({
            ServerEvent.RequestEntityInsEvent: self.RequestEntityInsEvent,
            ServerEvent.ServerModuleFinishedLoadEvent: self.ServerModuleFinishedLoadEvent,
        })

    # -----------------------------------------------------------------------------------

    def RegisterMobClass(self, engine_type, mob_class):
        """添加生物类"""
        if engine_type not in self.mob_class_map:
            self.mob_class_map[engine_type] = set()
        class_set = self.mob_class_map[engine_type]  # type: set
        class_set.add(mob_class)

    def AddMobIns(self, entity_id, ins_id):
        # type: (str, ModuleEntityPreset) -> None
        """动态添加生物实例"""
        if entity_id not in self.entity_storage:
            self.entity_storage[entity_id] = {}
        entity_storage = self.entity_storage[entity_id]
        entity_storage[id(ins_id)] = ins_id

    def DelMobIns(self, entity_id, ins_id):
        # type: (str, str) -> None
        """动态删除生物实例"""
        entity_storage = self.entity_storage.get(entity_id)  # type: dict
        if not entity_storage:
            return
        entity_ins = entity_storage.pop(ins_id, None)  # type: ModuleEntityPreset
        if not entity_ins:
            return
        entity_ins.OnDestroy()
        if not entity_storage:
            self.entity_storage.pop(entity_id, None)

    def RegisterHitDetection(self, entity_id):
        # type: (str) -> bool
        """注册碰撞检测"""
        if entity_id not in self.entity_storage:
            return False
        if self.comp_factory.CreatePlayer(entity_id).OpenPlayerHitMobDetection():
            self.hit_recall.add(entity_id)
            return True
        return False

    def UnRegisterHitDetection(self, entity_id):
        # type: (str) -> bool
        """反注册碰撞检测"""
        if entity_id not in self.hit_recall:
            return False
        return self.comp_factory.CreatePlayer(entity_id).ClosePlayerHitMobDetection()

    # -----------------------------------------------------------------------------------

    def OnAddMobIns(self, entity_id, engine_type):
        # type: (str, str) -> bool
        """添加生物实例"""
        if engine_type not in self.mob_class_map:
            return False
        class_set = self.mob_class_map[engine_type]  # type: set
        storage = {}
        for entity_class in class_set:
            ins = entity_class(entity_id)
            storage[id(ins)] = ins
        self.entity_storage[entity_id] = storage
        return True

    def OnServerAddMobInsEvent(self, entity_id, engineTypeStr):
        self.OnAddMobIns(entity_id, engineTypeStr)

    def OnServerAddPlayerInsEvent(self, playerId):
        if self.OnAddMobIns(playerId, "minecraft:player"):
            entity_storage = self.entity_storage.get(playerId)  # type: dict
            for entity_ins in entity_storage.values():
                if hasattr(entity_ins, "LoadData"):
                    entity_ins.LoadData()

    def TriggerTargetFunc(self, entity_id, key, *args, **kwargs):
        # type: (str, str, any, any) -> None
        """触发目标方法"""
        entity_storage = self.entity_storage.get(entity_id)  # type: dict
        if not entity_storage:
            return

        for entity_ins in entity_storage.values():
            func = getattr(entity_ins, key)
            if callable(func):
                func(*args, **kwargs)

    def DelEntityInstance(self, entity_id):
        """回收生物实体资源"""
        entity_storage = self.entity_storage.pop(entity_id, None)  # type: dict
        if not entity_storage:
            return
        for entity_ins in entity_storage.values():
            entity_ins.OnDestroy()
        if entity_id in self.hit_recall:
            self.hit_recall.discard(entity_id)
            self.comp_factory.CreatePlayer(entity_id).ClosePlayerHitMobDetection()

    def OnUpdateSecond(self):
        self._second5 += 1
        if self._second5 % 5 != 0:
            return
        for entity_id, entity_storage in self.entity_storage.items():
            # 回收不存活的实体
            entity_list = entity_storage.values()
            entity_ins = entity_list[0]  # type: ModuleEntityPreset
            if not entity_ins.IsPlayer() and not entity_ins.IsAlive():
                # print "[warn]", "不存活实体回收：%s" % entity_id
                self.DelEntityInstance(entity_id)

    # -----------------------------------------------------------------------------------

    """实体逻辑相关"""

    def DamageEvent(self, args):
        self.TriggerTargetFunc(args["srcId"], "OnDealDamage", args)
        self.TriggerTargetFunc(args["entityId"], "OnTookDamage", args)

    def MobDieEvent(self, args):
        victim_id = args["id"]
        killer_id = args["attacker"]
        self.TriggerTargetFunc(victim_id, "OnDeath", killer_id)
        self.TriggerTargetFunc(killer_id, "OnKillEntity", victim_id)

    def ActuallyHurtServerEvent(self, args):
        srcId = args["srcId"]
        vicId = args["entityId"]
        if args["damage"] > 0:
            self.TriggerTargetFunc(srcId, "OnActuallyDealDamage", args)
            if args["damage"] > 0:
                if RawEntity.GetHealth(vicId) - args["damage"] <= 0:
                    self.TriggerTargetFunc(vicId, "OnWillDie", args)
                    if not args["damage"] > 0:
                        return
                self.TriggerTargetFunc(vicId, "OnActuallyTookDamage", args)

    def EntityDefinitionsEventServerEvent(self, args):
        self.TriggerTargetFunc(args["entityId"], "OnTriggerEvent", args["eventName"])

    def PlayerDoInteractServerEvent(self, args):
        self.TriggerTargetFunc(args["interactEntityId"], "OnInteractedByPlayer", args["playerId"], args["itemDict"])

    def HealthChangeBeforeServerEvent(self, args):
        if args["cancel"]:
            return
        delta = int(args["to"] - args["from"])
        self.TriggerTargetFunc(args["entityId"], "OnFinalAddHealth" if delta > 0 else "OnFinalDelHealth", delta)

    # -----------------------------------------------------------------------------------

    """实体加载相关"""

    def PlayerIntendLeaveServerEvent(self, args):
        player_id = args.get("playerId")
        self.DelEntityInstance(player_id)

    def ClientLoadAddonsFinishServerEvent(self, args):
        playerId = args["playerId"]
        if not self.flag_finished_load:
            self.dirty_entity.add(playerId)
            return
        self.OnServerAddPlayerInsEvent(playerId)

    def AddEntityServerEvent(self, args):
        # type: (dict) -> None
        """服务端实体添加事件"""
        entity_id = args["id"]
        engine_type = args["engineTypeStr"]
        if args.get("cancel"):
            self.system.DestroyEntity(entity_id)
            return
        if not RawEntity.IsMob(entity_id):
            return
        if not self.flag_finished_load:
            self.dirty_entity.add(entity_id)
            return
        if not self.entity_getter(entity_id):
            self.OnServerAddMobInsEvent(entity_id, engine_type)

    def EntityRemoveEvent(self, args):
        # type: (dict) -> None
        """服务端实体移除事件"""
        entity_id = args.get("id")
        self.DelEntityInstance(entity_id)

    def ChunkAcquireDiscardedServerEvent(self, args):
        """服务端区块即将卸载事件"""
        entities = args.get("entities")
        if not entities:
            return
        # 回收生物实例
        for entity_id in entities:
            self.DelEntityInstance(entity_id)
            # print "[suc]", "区块卸载实体回收：%s" % entity_id

    def RequestEntityInsEvent(self, args):
        """
        请求生物实例\n
        - entityId: str
        - class_name: str
        """
        entity_id = args["entityId"]
        class_name = args["class_name"]
        entity_storage = self.entity_storage.get(entity_id)  # type: dict
        if not entity_storage:
            return
        if not class_name:
            args["ins"] = entity_storage.values()
            return
        for entity_ins in entity_storage.values():
            if entity_ins.__class__.__name__ == class_name:
                args["ins"] = entity_ins
                return

    # -----------------------------------------------------------------------------------

    def OnMobHitMobServerEvent(self, args):
        entity_id = args["mobId"]
        if entity_id not in self.hit_recall:
            return
        mob_list = args["hittedMobList"]  # type: list
        storage = self.entity_storage.get(entity_id)  # type: dict
        for engine_ins in storage.values():
            engine_ins.OnHitRecall(mob_list)

    def ServerModuleFinishedLoadEvent(self, _):
        def active():
            if not self.mob_class_map:
                print "[warn]", "empty mob class map! destroying mob module server."
                self.ModuleSystem.DelModule(ModuleEnum.identifier)
                return
            self.flag_finished_load = True
            for entity_id in self.dirty_entity:
                if RawEntity.IsPlayer(entity_id):
                    self.OnServerAddPlayerInsEvent(entity_id)
                else:
                    self.OnServerAddMobInsEvent(entity_id, RawEntity.GetTypeStr(entity_id))
            self.dirty_entity.clear()
            self.ModuleSystem.RegisterUpdateSecond(self.OnUpdateSecond)

        self.DelayTickFunc(30, active)
