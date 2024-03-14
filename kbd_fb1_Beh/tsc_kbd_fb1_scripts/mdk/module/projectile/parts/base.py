# -*- coding:utf-8 -*-


from ....server.system.base import *
from mod.common.utils.mcmath import Vector3


class ProjectileInterface(object):
    """抛射物接口"""
    __mVersion__ = 2

    def OnProjectileHit(self, hit_pos):
        # type: (tuple) -> bool
        """碰撞回调"""

    def OnHitEntity(self, entity_id, hit_pos):
        # type: (str, tuple) -> bool
        """碰撞生物回调"""

    def OnHitBlock(self, hit_pos, block_pos, hit_face):
        # type: (tuple, tuple, int) -> bool
        """碰撞方块回调"""

    def OnProjectileRemove(self, entity_id):
        # type: (str) -> None
        """抛射物移除时触发"""

    def OnProjectileCritHit(self, entity_id, target_id):
        # type: (str, str) -> None
        """抛射物暴击触发"""


class ProjectileBase(ProjectileInterface):
    """抛射物基类"""
    __mVersion__ = 3

    def __init__(self, engine_type, particle=None, param=None):
        self.comp_factory = serverApi.GetEngineCompFactory()
        self.projectile_comp = self.comp_factory.CreateProjectile(serverApi.GetLevelId())

        self.engine_type = engine_type
        self.particle = particle
        self.param = param  # type: dict
        if not self.param:
            self.param = {}

    _projectile_module = None

    @property
    def ProjectileModule(self):
        # type: () -> MDKConfig.GetPresetModule().ProjectileModuleServer
        if ProjectileBase._projectile_module:
            return ProjectileBase._projectile_module
        module_key = MDKConfig.GetPresetModule().ProjectileModuleServer.GetId()
        module = MDKConfig.GetModuleServer().GetModule(module_key)
        if not module:
            return None
        ProjectileBase._projectile_module = weakref.proxy(module)
        return ProjectileBase._projectile_module

    # -----------------------------------------------------------------------------------

    """创建相关"""

    # 创建抛射物
    def Create(self, *args, **kwargs):
        """创建抛射物"""

    # 根据自定义参数创建抛射物
    def CreateFromParam(self, owner, param):
        entity_id = self.projectile_comp.CreateProjectileEntity(owner, self.engine_type, param)
        if not entity_id:
            print "[error]", "创建抛射物失败：%s" % self.engine_type
            return None
        self.ProjectileModule.RegisterProjectile(entity_id, self)
        return entity_id

    # 朝向目标创建抛射物
    def CreateFacingTarget(self, *args, **kwargs):
        """朝向目标创建抛射物"""

    # 使用玩家朝向创建
    def CreateFromPlayer(self, owner, on_eye=True, horizon=False):
        """使用玩家朝向创建"""
        self.direction = RawEntity.GetDrt(owner, horizon)
        self.position = RawEntity.GetPos(owner, on_eye)
        entity_id = self.projectile_comp.CreateProjectileEntity(owner, self.engine_type, self.param)
        if not entity_id:
            print "[error]", "创建抛射物失败：%s" % self.engine_type
            return None
        self.ProjectileModule.RegisterProjectile(entity_id, self)
        return entity_id

    # -----------------------------------------------------------------------------------

    """朝向相关"""

    # 设置抛射物朝向目标
    def SetFacingTarget(self, spawn_pos, target):
        # type: (tuple, any) -> None
        """设置抛射物朝向目标"""
        if isinstance(target, tuple):
            self.SetFacingTargetPos(spawn_pos, target)
        else:
            self.SetFacingTargetEntity(spawn_pos, target)

    # 设置抛射物对准目标实体
    def SetFacingTargetEntity(self, spawn_pos, target_id):
        # type: (tuple, str) -> None
        """设置抛射物对准目标实体"""
        self.position = spawn_pos
        target_pos = RawEntity.GetCollisionPos(target_id, ry=1.0)
        self.direction = self.GetFacingVec(spawn_pos, target_pos)

    # 设置抛射物对准目标位置
    def SetFacingTargetPos(self, spawn_pos, target_pos):
        # type: (tuple, tuple) -> None
        """设置抛射物对准目标位置"""
        self.position = spawn_pos
        self.direction = self.GetFacingVec(spawn_pos, target_pos)

    # 获得朝向目标的向量
    @staticmethod
    def GetFacingVec(src, des):
        # type: (tuple, tuple) -> tuple
        """获得朝向目标的向量"""
        try:
            vector = Vector3(des)
            vector -= Vector3(src)
            vector = vector.Normalized()  # type: Vector3
            return vector.ToTuple()
        except ValueError:
            print "[info]", "输入参数错误：", des
            return 0, 0, 0

    # -----------------------------------------------------------------------------------

    @property
    def position(self):
        """初始位置"""
        return self.param.get("position", (0, 0, 0))

    @position.setter
    def position(self, value):
        # type: (tuple) -> None
        """初始位置"""
        self.param["position"] = value

    @property
    def direction(self):
        """初始朝向"""
        return self.param.get("direction", (0, 0, 0))

    @direction.setter
    def direction(self, value):
        # type: (tuple) -> None
        """初始朝向"""
        self.param["direction"] = value

    @property
    def power(self):
        """投掷的力量值"""
        return self.param.get("power", 1.0)

    @power.setter
    def power(self, value):
        # type: (float) -> None
        """投掷的力量值"""
        self.param["power"] = value

    @property
    def gravity(self):
        """抛射物重力因子，默认为json配置中的值"""
        return self.param.get("gravity", 0.05)

    @gravity.setter
    def gravity(self, value):
        # type: (float) -> None
        """抛射物重力因子，默认为json配置中的值"""
        self.param["gravity"] = value

    @property
    def damage(self):
        """抛射物伤害值，默认为json配置中的值"""
        return self.param.get("damage", 1)

    @damage.setter
    def damage(self, value):
        # type: (float) -> None
        """抛射物伤害值，默认为json配置中的值"""
        self.param["damage"] = value

    @property
    def target_id(self):
        """抛射物目标（指定了target之后，会和潜影贝生物发射的跟踪导弹的那个投掷物是一个效果），默认不指定"""
        return self.param.get("target_id")

    @target_id.setter
    def target_id(self, value):
        # type: (str) -> None
        """抛射物目标（指定了target之后，会和潜影贝生物发射的跟踪导弹的那个投掷物是一个效果），默认不指定"""
        self.param["targetId"] = value

    @property
    def is_damage_owner(self):
        """对创建者是否造成伤害，默认不造成伤害"""
        return self.param.get("is_damage_owner", False)

    @is_damage_owner.setter
    def is_damage_owner(self, value):
        # type: (bool) -> None
        """对创建者是否造成伤害，默认不造成伤害"""
        self.param["isDamageOwner"] = value

    @property
    def is_destroy_on_hit(self):
        # type: () -> bool
        """是否碰撞销毁"""
        if "destroyOnHit" not in self.param:
            return True
        return self.param["destroyOnHit"]

    @is_destroy_on_hit.setter
    def is_destroy_on_hit(self, value):
        # type: (bool) -> None
        """是否碰撞销毁"""
        self.param["destroyOnHit"] = value
