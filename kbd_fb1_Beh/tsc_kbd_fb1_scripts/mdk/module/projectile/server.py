# -*- coding:utf-8 -*-


from const import *
from parts.base import ProjectileBase
from parts.linear_projectile import LinearProjectile
from parts.track_projectile import TrackingProjectile
from ..system.base import *


class ProjectileModuleServer(ModuleServerBase):
    """抛射物模块服务端"""
    __mVersion__ = 2
    __identifier__ = ModuleEnum.identifier

    def __init__(self):
        super(ProjectileModuleServer, self).__init__()
        self.projectile_map = {}
        self.projectile_cache = {}
        self.projectile_storage = {}

    def ConfigEvent(self):
        super(ProjectileModuleServer, self).ConfigEvent()
        self.defaultEvent.update({
            ServerEvent.ProjectileDoHitEffectEvent: self.ProjectileDoHitEffectEvent,
            ServerEvent.ProjectileCritHitEvent: self.ProjectileCritHitEvent,
            ServerEvent.EntityRemoveEvent: self.EntityRemoveEvent,
        })

    def RegisterProjectile(self, entity_id, projectile_ins):
        # type: (str, ProjectileBase) -> None
        """注册抛射物"""
        projectile_id = id(projectile_ins)
        self.projectile_cache[projectile_id] = projectile_ins
        self.projectile_map[entity_id] = projectile_id
        if projectile_id not in self.projectile_storage:
            self.projectile_storage[projectile_id] = set()
        storage = self.projectile_storage[projectile_id]  # type: set
        storage.add(entity_id)

    def CreateTrackProjectile(self, engine_type, particle=None, param=None):
        # type: (str, tuple, dict) -> TrackingProjectile
        """创建一个追踪抛射物"""
        projectile = TrackingProjectile(engine_type, particle, param)
        self.projectile_cache[id(projectile)] = projectile
        return projectile

    def CreateLinearProjectile(self, engine_type, particle=None, param=None):
        # type: (str, tuple, dict) -> LinearProjectile
        """创建一个直线抛射物"""
        projectile = LinearProjectile(engine_type, particle, param)
        self.projectile_cache[id(projectile)] = projectile
        return projectile

    # -----------------------------------------------------------------------------------

    def ProjectileDoHitEffectEvent(self, args):
        entity_id = args["id"]
        projectile_id = self.projectile_map.get(entity_id)
        if not projectile_id:
            return
        projectile = self.projectile_cache[projectile_id]  # type: ProjectileBase
        # 碰撞类型
        hit_type = args["hitTargetType"]
        hit_pos = (args["x"], args["y"], args["z"])
        if projectile.OnProjectileHit(hit_pos):
            return
        if hit_type == "ENTITY":
            hit_target = args["targetId"]
            if projectile.OnHitEntity(hit_target, hit_pos):
                return
        else:
            hit_face = args["hitFace"]
            block_pos = (args["blockPosX"], args["blockPosY"], args["blockPosZ"])
            if projectile.OnHitBlock(hit_pos, block_pos, hit_face):
                return
        if projectile.is_destroy_on_hit:
            self.system.DestroyEntity(entity_id)

    def EntityRemoveEvent(self, args):
        entity_id = args["id"]
        projectile_id = self.projectile_map.pop(entity_id, None)
        if not projectile_id:
            return
        projectile_ins = self.projectile_cache.get(projectile_id)  # type: ProjectileBase
        projectile_ins.OnProjectileRemove(entity_id)

        storage = self.projectile_storage.get(projectile_id)  # type: set
        storage.discard(entity_id)
        if not storage:
            self.projectile_storage.pop(projectile_id, None)
            self.projectile_cache.pop(projectile_id, None)

    def ProjectileCritHitEvent(self, args):
        entity_id = args["id"]
        target_id = args["targetId"]

        projectile_id = self.projectile_map.get(entity_id)
        if not projectile_id:
            return
        projectile_ins = self.projectile_cache.get(projectile_id)  # type: ProjectileBase
        projectile_ins.OnProjectileCritHit(entity_id, target_id)
