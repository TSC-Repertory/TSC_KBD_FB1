# -*- coding:utf-8 -*-


import mod.server.extraServerApi as serverApi

from raw_entity import RawEntity
from skill_entity import SkillEntity
from ...common.system.base import ServerEvent, GameEntity
from ...decorator.identifier import check_id
from ...loader import MDKConfig


class ProjectileEntity(SkillEntity):
    """抛射物实体基类"""
    __mVersion__ = 10
    ParamKeyDefine = ["position", "direction", "power", "gravity", "damage", "targetId", "isDamageOwner"]

    def __init__(self, entityId, **kwargs):
        super(ProjectileEntity, self).__init__(entityId)
        self.__namespace = serverApi.GetEngineNamespace()
        self.__system_name = serverApi.GetEngineSystemName()

        self.pack = kwargs
        self.hitType = None
        self.hitTarget = None

        self._hitPos = None
        self._sourceId = "-1"

        self._hit_recall = None
        self._hit_target_recall = None
        self._hit_block_recall = None

        self._destroy_recall = None
        self._destroy_on_hit = self.pack.get("destroy_on_hit", True)
        self._detecting = False

        self._state_destroy = False

        self.owner = None
        self.hit_sound = self.pack.get("hit_sound")
        if "spawn_sound" in self.pack:
            RawEntity.PlaySound(self.pack["spawn_sound"], self.foot_pos)
        if "destroy" in self.pack:
            self.Destroy(self.pack["destroy"])

    def __del__(self):
        # print "[warn]", "del:%s" % self.__class__.__name__
        pass

    def _Destroy(self):
        if self._state_destroy:
            return
        self._state_destroy = True
        if self._detecting:
            self._UnListenEvent()
        if self._destroy_recall:
            self._destroy_recall(self)
            del self._destroy_recall
        del self._hit_recall
        del self._hit_target_recall
        del self._hit_block_recall
        super(ProjectileEntity, self)._Destroy()

    # -----------------------------------------------------------------------------------

    @classmethod
    def CreateFromEntity(cls, engine_type, entityId, **kwargs):
        # type: (any, str, str, any) -> ProjectileEntity
        """
        用实体信息创建抛射物\n
        ------------------------\n
        -- 可传参数: \n
        - position: tuple(float,float,float)	初始位置
        - direction: tuple(float,float,float)	初始朝向
        - power: float	投掷的力量值
        - gravity: float	抛射物重力因子，默认为json配置中的值
        - damage: float	抛射物伤害值，默认为json配置中的值
        - targetId: str	抛射物目标（指定了target之后，会和潜影贝生物发射的跟踪导弹的那个投掷物是一个效果），默认不指定
        - isDamageOwner: bool	对创建者是否造成伤害，默认不造成伤害
        """
        param = RawEntity.GetInfoForProjectile(entityId, kwargs.get("horizon", True))
        if kwargs:
            param.update(kwargs)
        projectile = cls.CreateProjectile(engine_type, entityId, param)
        projecowner = entityId
        return projectile

    @classmethod
    def CreateProjectile(cls, engine_type, spawner_id, param):
        # type: (any, str, str, dict) -> ProjectileEntity
        """创建抛射物"""
        projectile_comp = serverApi.GetEngineCompFactory().CreateProjectile(serverApi.GetLevelId())
        entity_id = projectile_comp.CreateProjectileEntity(spawner_id, engine_type, param)
        return ProjectileEntity(entity_id, **param)

    # -----------------------------------------------------------------------------------

    def IsDestroyOnHit(self):
        # type: () -> bool
        """是否碰撞销毁"""
        return self._destroy_on_hit

    # -----------------------------------------------------------------------------------

    def GetSourceId(self):
        # type: () -> str
        """获取创建者Id"""
        return self._sourceId

    def GetHitPos(self):
        """获取击中位置"""
        return self._hitPos

    # -----------------------------------------------------------------------------------

    def ConfigHitRecall(self, recall):
        # type: (any) -> ProjectileEntity
        """设置抛射物击中回调"""
        if not self._detecting:
            self._detecting = True
            self._ListenEvent()
        self._hit_recall = recall
        return self

    def ConfigDestroyRecall(self, recall):
        # type: (any) -> None
        """设置抛射物销毁时回调"""
        self._destroy_recall = recall

    def ConfigDestroyOnHit(self, isOn):
        # type: (bool) -> ProjectileEntity
        """
        设置击中销毁\n
        默认开启，持续需要关闭此属性\n
        Json配置<destroy_on_hurt>为 False
        """
        self._destroy_on_hit = isOn
        return self

    def ConfigHitTargetRecall(self, recall):
        # type: (any) -> ProjectileEntity
        """
        设置抛射物击中生物回调\n
        - 回调传入击中生物Id
        - entityId: str
        """
        if not self._detecting:
            self._detecting = True
            self._ListenEvent()
        self._hit_target_recall = recall
        return self

    def ConfigHitBlockRecall(self, recall):
        # type: (any) -> ProjectileEntity
        """
        设置抛射物击中方块回调\n
        - 回调传入击中位置
        - hitPos: tuple
        """
        if not self._detecting:
            self._detecting = True
            self._ListenEvent()
        self._hit_block_recall = recall
        return self

    # -----------------------------------------------------------------------------------

    def ShuntDownListen(self):
        """关闭监听"""
        self._UnListenEvent()

    # -----------------------------------------------------------------------------------

    def _ListenEvent(self):
        system = MDKConfig.GetModuleServer()
        for event, recall in {
            ServerEvent.ProjectileDoHitEffectEvent: self._ProjectileDoHitEffectEvent,
            ServerEvent.EntityRemoveEvent: self._EntityRemoveEvent,
        }.iteritems():
            system.ListenForEvent(self.__namespace, self.__system_name, event, self, recall, 10)

    def _UnListenEvent(self):
        system = MDKConfig.GetModuleServer()
        for event, recall in {
            ServerEvent.ProjectileDoHitEffectEvent: self._ProjectileDoHitEffectEvent,
            ServerEvent.EntityRemoveEvent: self._EntityRemoveEvent,
        }.iteritems():
            system.UnListenForEvent(self.__namespace, self.__system_name, event, self, recall, 10)

    @check_id
    def _ProjectileDoHitEffectEvent(self, args):
        # type: (dict) -> None
        """
        触发时机：当抛射物碰撞时触发该事件\n
        - id: str 子弹id
        - hitTargetType: str 碰撞目标类型,ENTITY或是BLOCK
        - targetId: str 碰撞目标id
        - hitFace: int 撞击在方块上的面id，参考Facing枚举
        - x: float 碰撞x坐标
        - y: float 碰撞y坐标
        - z: float 碰撞z坐标
        - blockPosX: int 碰撞是方块时，方块x坐标
        - blockPosY: int 碰撞是方块时，方块y坐标
        - blockPosZ: int 碰撞是方块时，方块z坐标
        - srcId: str 创建者id
        """
        if self._state_destroy:
            return
        if RawEntity.GetTypeStr(args["targetId"]) in [GameEntity.projectile, GameEntity.detector]:
            return
        self._sourceId = args.get("srcId", -1)
        self._hitPos = (args.get("x"), args.get("y"), args.get("z"))
        if self.hit_sound:
            RawEntity.PlaySound(self.hit_sound, self._hitPos)
            self.hit_sound = None

        if args.get("hitTargetType") == "BLOCK":
            self.hitType = "BLOCK"
            self.hitTarget = (args.get("blockPosX"), args.get("blockPosY"), args.get("blockPosZ"))
            if self._hit_block_recall:
                self._hit_block_recall(self._hitPos)
        else:
            self.hitTarget = args.get("targetId")
            self.hitType = "ENTITY"
            if self._hit_target_recall:
                self._hit_target_recall(self.hitTarget)

        if hasattr(self, "_hit_recall") and self._hit_recall:
            self._hit_recall(self)
        if self._destroy_on_hit:
            self._Destroy()

    @check_id
    def _EntityRemoveEvent(self, _):
        if self._state_destroy:
            return
        self._Destroy()
