# -*- coding:utf-8 -*-


from base import *


class TrackingProjectile(ProjectileBase):
    """追踪抛射物"""
    __mVersion__ = 2

    # 创建抛射物
    def Create(self, owner, target):
        self.target_id = target
        entity_id = self.projectile_comp.CreateProjectileEntity(owner, self.engine_type, self.param)
        if not entity_id:
            print "[error]", "创建抛射物失败：%s" % self.engine_type
            return None
        self.ProjectileModule.RegisterProjectile(entity_id, self)
        return entity_id

    # 朝向目标创建抛射物
    def CreateFacingTarget(self, owner, spawn_pos, target):
        """朝向目标创建抛射物"""
        self.target_id = target
        self.SetFacingTarget(spawn_pos, target)
        entity_id = self.projectile_comp.CreateProjectileEntity(owner, self.engine_type, self.param)
        if not entity_id:
            print "[error]", "创建抛射物失败：%s" % self.engine_type
            return None
        self.ProjectileModule.RegisterProjectile(entity_id, self)
        return entity_id
