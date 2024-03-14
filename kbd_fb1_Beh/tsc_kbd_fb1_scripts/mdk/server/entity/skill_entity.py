# -*- coding:utf-8 -*-


import math

import mod.server.extraServerApi as serverApi
from mod.common.minecraftEnum import ActorDamageCause
from mod.common.utils.mcmath import Vector3

from attr_entity import AttrEntity
from entity import Entity
from raw_entity import RawEntity
from ...common.system.base import GameEntity, GameFilter
from ...common.utils.misc import Misc
from ...loader import MDKConfig


class SkillEntity(AttrEntity):
    """技能实体基类"""
    __mVersion__ = 7

    def __init__(self, entityId):
        super(SkillEntity, self).__init__(entityId)
        self._trackGen = None

    @staticmethod
    def CastEffect(victimId, effectName, duration=10, amplifier=0, showParticles=True):
        """释放药水效果"""
        return RawEntity.AddEffect(victimId, effectName, duration, amplifier, showParticles)

    # -----------------------------------------------------------------------------------

    def SetRangeDamage(self, damage, radius, banList=None, knocked=False, **kwargs):
        # type: (int, int, list, bool, any) -> None
        """设置范围伤害"""
        if not banList:
            mobSet = set(self.GetMobInRadius(radius, **kwargs))
            mobSet.discard(self.id)
            for victimId in mobSet:
                self.SetInstantDamage(victimId, damage, knocked=knocked, **kwargs)
        else:
            for victimId in self.GetMobInRadius(radius, **kwargs):
                if victimId in banList:
                    continue
                self.SetInstantDamage(victimId, damage, knocked=knocked, **kwargs)

    def SetRangeDamageAtPos(self, damage, radius, pos, **kwargs):
        """设置定点范围伤害"""
        for victimId in self.GetMobAtPos(pos, radius, **kwargs):
            self.SetInstantDamage(victimId, damage, **kwargs)

    def SetInstantDamage(self, victimId, damage, **kwargs):
        """对实体造成瞬间伤害\n
        可传参数：\n
        - cause: 伤害类型
        - attacker: str 攻击者
        - knocked: bool 是否击退
        :param victimId: str 受伤实体Id
        :param damage: int 伤害值
        """
        if not self.game_comp.IsEntityAlive(victimId):
            return
        damage = max(math.trunc(damage), 1)
        cause = kwargs.get("cause", ActorDamageCause.Override)
        attacker = kwargs.get("attacker", self.id)
        knocked = kwargs.get("knocked", False)

        hurComp = self.comp_factory.CreateGame(victimId)
        hurComp.SetHurtCD(0)
        self.comp_factory.CreateHurt(victimId).Hurt(damage, cause, attacker, knocked=knocked)
        hurComp.SetHurtCD(10)

    def SetInstanceRangeDamage(self, radius, damage, **kwargs):
        """设置瞬间范围伤害
        :param radius: int 方形范围半径
        :param damage: int | float 攻击值
        :return:
        """
        forward = kwargs.get("forward")
        if not forward:
            modList = self.GetMobInRadius(radius, **kwargs)
        else:
            targetId = kwargs.get("detector", self.id)
            atPos = RawEntity.GetPos(targetId)
            atDrt = RawEntity.GetDrt(targetId)
            checkPos = Misc.GetPosModify(atPos, (atDrt[0] * forward, 0, atDrt[2] * forward))
            kwargs.pop("forward", None)
            modList = self.GetMobAtPos(checkPos, radius, **kwargs)

        for victimId in modList:
            self.SetInstantDamage(victimId, damage, **kwargs)

    def SetContinueDamage(self, victimId, sumDamage, sumTime, damageTime=1, **kwargs):
        """设置一个持续伤害的定时器 多个持续伤害可叠加\n
        :param victimId: 被攻击者ID
        :param sumDamage: 攻击伤害总量
        :param sumTime: 持续时间
        :param damageTime: 伤害次数
        """
        damage = float(sumDamage) / damageTime
        delay = int(30 * float(sumTime) / damageTime)

        damageConfig = {
            "attacker": kwargs.get("attacker", self.id),
            "cause": kwargs.get("cause", ActorDamageCause.Override),
            "knocked": kwargs.get("knocked", False)
        }

        def active():
            for _ in xrange(damageTime):
                if RawEntity.IsAlive(victimId):
                    self.SetInstantDamage(victimId, damage, **damageConfig)
                yield delay

        callback = kwargs.get("callback")
        if not callable(callback):
            callback = None
        MDKConfig.GetModuleServer().StartCoroutine(active, callback)

    def SetRangeContinueDamage(self, atPos, sumDamage, sumTime=1.0, damageTime=1, radius=3, **kwargs):
        """设置一个持续伤害的定时器 多个持续伤害可叠加\n
        可传参数：\n
        -- banList: list无敌列表\n
        -- damageOnce: bool只攻击一次\n
        -- attacker: 攻击者ID\n
        -- filters: 生物过滤器[默认：怪物过滤器]\n
        -- effectList: list药水效果字典\n
        --- potion(effectName, duration, amplifier, isShow)

        :param atPos: tuple 技能释放位置
        :param sumDamage: 攻击伤害总量
        :param sumTime: float 持续时间
        :param damageTime: int 伤害次数
        :param radius: 攻击范围
        """
        if atPos is None:
            atPos = self.foot_pos
        attackId = kwargs.get("attacker", self.id)
        system = MDKConfig.GetModuleServer()
        detectorId = system.CreateEngineEntityByTypeStr(GameEntity.detector, atPos, (0, 0), self.dim)
        self.game_comp.AddTimer(sumTime + 0.1, system.DestroyEntity, detectorId)
        self.comp_factory.CreatePersistence(detectorId).SetPersistence(False)
        damageOnce = kwargs.get("damageOnce", False)
        effectList = kwargs.get("effectList", [])
        banList = kwargs.get("banList", [self.id])  # type: list

        delay = 30 * float(sumTime) / damageTime
        damage = float(sumDamage) / damageTime
        filters = kwargs.get("filters", GameFilter.Mob)
        damageConfig = {
            "attacker": attackId,
            "cause": kwargs.get("cause", ActorDamageCause.Override),
            "knocked": kwargs.get("knocked", False)
        }

        def active():
            for _ in xrange(damageTime):
                for victimId in self.GetMobAtPos(atPos, radius, detectorId=detectorId, filters=filters):
                    if victimId in banList:
                        continue
                    if damageOnce:
                        banList.append(victimId)
                    self.SetInstantDamage(victimId, damage, **damageConfig)
                    for effectConfig in effectList:
                        self.CastEffect(victimId, **effectConfig)
                yield delay

        def destroy():
            callback = kwargs.get("callback")
            if callable(callback):
                callback()
            system.DestroyEntity(detectorId)

        MDKConfig.GetModuleServer().StartCoroutine(active, destroy)

    def SetRangeContinueDamageSingle(self, atPos, damage, sumTime, delay=1, radius=3, **kwargs):
        """设置一个持续伤害的定时器 多个持续伤害可叠加\n
        可传参数：\n
        -- banList: list无敌列表\n
        -- damageOnce: bool只攻击一次\n
        -- attacker: 攻击者ID\n
        -- filters: 生物过滤器[默认：怪物过滤器]\n
        -- effectList: list药水效果字典\n
        --- potion(effectName, duration, amplifier, isShow)

        :param atPos: tuple 技能释放位置（传None则使用实体位置）
        :param damage: int 每次攻击的伤害
        :param sumTime: float 持续多少秒
        :param delay: float 每隔多少秒伤害一次
        :param radius: int 攻击范围
        """
        if atPos is None:
            atPos = self.foot_pos
        attackId = kwargs.get("attacker", self.id)
        system = MDKConfig.GetModuleServer()
        detectorId = system.CreateEngineEntityByTypeStr(GameEntity.detector, atPos, (0, 0), self.dim)
        self.comp_factory.CreatePersistence(detectorId).SetPersistence(False)
        damageOnce = kwargs.get("damageOnce", False)
        effectList = kwargs.get("effectList", [])
        banList = kwargs.get("banList", [self.id])
        assert isinstance(banList, list)

        damageTime = int(float(sumTime) / delay)
        delay = int(delay * 30)
        filters = kwargs.get("filters", GameFilter.Mob)
        damageConfig = {
            "attacker": attackId,
            "cause": kwargs.get("cause", ActorDamageCause.Override),
            "knocked": kwargs.get("knocked", False)
        }

        def active():
            for _ in xrange(damageTime):
                for victimId in self.GetMobAtPos(atPos, radius, detectorId=detectorId, filters=filters):
                    if victimId in banList:
                        continue
                    if damageOnce:
                        banList.append(victimId)
                    self.SetInstantDamage(victimId, damage, **damageConfig)
                    for effectConfig in effectList:
                        self.CastEffect(victimId, **effectConfig)
                yield delay

        def destroy():
            system.DestroyEntity(detectorId)
            callback = kwargs.get("callback")
            if callable(callback):
                callback()

        MDKConfig.GetModuleServer().StartCoroutine(active, destroy)

    # -----------------------------------------------------------------------------------

    """动量相关"""

    def SetPowerMotion(self, motion, power):
        # type: (tuple, float) -> None
        """设置乘积动量"""
        vector = Vector3(*motion)
        vector *= power
        self.comp_factory.CreateActorMotion(self.id).SetMotion(vector.ToTuple())

    # -----------------------------------------------------------------------------------

    def ResetMotion(self):
        """重置动量"""
        self.comp_factory.CreateActorMotion(self.id).ResetMotion()

    def SetForwardByKnock(self, power, drt=None, **kwargs):
        """设置实体前进动量 - 击退方式"""
        victimId = kwargs.get("victimId", self.id)
        height = kwargs.get("height", 0)
        if not drt:
            horizon = kwargs.get("horizon", True)
            rot = self.comp_factory.CreateRot(victimId).GetRot()
            drt = serverApi.GetDirFromRot((0 if horizon else rot[0], rot[1]))
        actionComp = self.comp_factory.CreateAction(victimId)
        actionComp.SetMobKnockback(drt[0], drt[2], power, height, height)

    def SetBackwardByKnock(self, power, **kwargs):
        """设置实体往后动量 - 击退方式"""
        height = kwargs.get("height", 0)
        maxHeight = kwargs.get("maxHeight", 0)

        rot = self.GetRot(dx=180)
        drt = serverApi.GetDirFromRot(rot)
        actionComp = self.comp_factory.CreateAction(self.id)
        actionComp.SetMobKnockback(drt[0], drt[2], power, height, maxHeight)

    def SetJumpByKnock(self, power, **kwargs):
        """设置跳跃"""
        victimId = kwargs.get("victimId", self.id)
        actionComp = self.comp_factory.CreateAction(victimId)
        height = kwargs.get("height", 1)
        actionComp.SetMobKnockback(0, 0, power, height, height)

    def SetDragDownByGravy(self, power, duration=0.5):
        """设置下降"""
        gravy = self.GetGravity()

        def active():
            self.SetGravity(-power)
            yield max(1, int(duration * 30))
            self.SetGravity(gravy)

        MDKConfig.GetModuleServer().StartCoroutine(active)

    def SetForwardByMotion(self, power, drt=None, motion=None, **kwargs):
        """设置实体动量 -动量方法"""
        victimId = kwargs.get("victimId", self.id)
        if not drt:
            horizon = kwargs.get("horizon", True)
            rot = self.comp_factory.CreateRot(victimId).GetRot()
            drt = serverApi.GetDirFromRot((0 if horizon else rot[0], rot[1]))
        if not motion:
            motion = (power * drt[0], 0, power * drt[2])
        self.comp_factory.CreateActorMotion(victimId).SetMotion(motion)

    def SetDragEntityToPos(self, victimId, onRange, maxPower=1.0, **kwargs):
        """设置在某点拉扯生物 距离越远的生物受力越小\n
        可传参数：\n
        - atPos: tuple施力位置
        :param victimId: 目标ID
        :param onRange: float 基础力范围
        :param maxPower: float 最大推力
        :return: None
        """
        if not self.game_comp.IsEntityAlive(victimId):
            return
        atPos = kwargs.get("atPos", self.GetPos())
        vicPos = self.comp_factory.CreatePos(victimId).GetPos()
        if not atPos or not vicPos:
            return
        distance = Misc.GetDistBetween(vicPos, atPos)

        rate = distance / onRange
        power = Misc.GetValueFromRate(rate, 0.2, maxPower)

        vec = Vector3(atPos)
        vec -= Vector3(vicPos)
        vec.Normalize()
        vec *= power
        motion = vec.ToTuple()

        if RawEntity.IsPlayer(victimId):
            height = kwargs.get("height", 0.2)
            self.comp_factory.CreateAction(victimId).SetMobKnockback(vec[0], vec[2], maxPower, height, height)
        self.comp_factory.CreateActorMotion(victimId).SetMotion(motion)

    def SetKnockEntityAtDrt(self, victimId, atDrt, maxPower=1, **kwargs):
        """设置向某方向击退生物"""
        if not self.game_comp.IsEntityAlive(victimId):
            return
        vicPos = self.comp_factory.CreatePos(victimId).GetPos()

        motionVec = Vector3(vicPos)
        motionVec += Vector3(atDrt)
        motionVec.Normalize()
        motionVec *= maxPower
        motion = motionVec.ToTuple()

        if RawEntity.IsPlayer(victimId):
            height = kwargs.get("height", motion[1] * maxPower * 0.5)
            self.comp_factory.CreateAction(victimId).SetMobKnockback(atDrt[0], atDrt[2], maxPower, height, height)
        self.comp_factory.CreateActorMotion(victimId).SetMotion(motion)

    def SetKnockEntityAtPos(self, victimId, onRange, maxPower=1.0, **kwargs):
        """设置在某点击退生物 距离越远的生物受力越小\n
        可传参数：\n
        - atPos: tuple施力位置
        :param victimId: 目标ID
        :param onRange: float 基础力范围
        :param maxPower: float 最大推力
        :return: None
        """
        if not self.game_comp.IsEntityAlive(victimId):
            return
        atPos = kwargs.get("atPos", self.foot_pos)
        vicPos = RawEntity.GetPos(victimId)
        if not atPos or not vicPos:
            return
        distance = Misc.GetDistBetween(vicPos, atPos)
        rate = onRange / distance if distance > 0 else 1
        power = Misc.GetValueFromRate(rate, 0.5, maxPower)

        motionVec = Vector3(vicPos)
        motionVec -= Vector3(atPos)
        motionVec.Normalize()
        motionVec *= power
        motion = motionVec.ToTuple()

        if RawEntity.IsPlayer(victimId):
            height = kwargs.get("height", motion[1] * power * 0.5)
            self.comp_factory.CreateAction(victimId).SetMobKnockback(motion[0], motion[2], power, height, height)
        else:
            self.comp_factory.CreateActorMotion(victimId).SetMotion(motion)

    def SetEntityFire(self, victimId, duration=5, damage=1, **kwargs):
        # type: (str, int, int, dict) -> None
        """设置实体着火"""
        self.comp_factory.CreateAttr(victimId).SetEntityOnFire(duration, damage)

    def SetTrackEntity(self, targetId, trackRot=False, forward=0.0, lifeTime=600):
        """设置实体跟随目标"""

        def active():
            targetEntity = Entity(targetId)
            for _ in xrange(lifeTime):
                yield 1
                if not targetEntity.IsAlive() or not self.IsAlive():
                    reset()
                    return
                if forward:
                    tPos = targetEntity.GetPosForward(forward)
                else:
                    tPos = targetEntity.foot_pos

                RawEntity.SetPos(self.id, tPos)
                if trackRot:
                    self.SetRot(RawEntity.GetRot(targetId))

        def reset():
            self._trackGen = None

        self._trackGen = MDKConfig.GetModuleServer().StartCoroutine(active, reset)
        return self

    def SetTrackEntityOffset(self, targetId, offset=None, lifeTime=600):
        """设置实体跟随目标"""

        def active():
            targetEntity = Entity(targetId)
            for _ in xrange(lifeTime):
                yield 1
                if not targetEntity.IsAlive() or not self.IsAlive():
                    reset()
                    return
                if offset:
                    tPos = targetEntity.GetModifyPos(False, *offset)
                else:
                    tPos = targetEntity.foot_pos
                RawEntity.SetPos(self.id, tPos)

        def reset():
            self._trackGen = None

        self._trackGen = MDKConfig.GetModuleServer().StartCoroutine(active, reset)
        return self

    def ResetTrackEntity(self):
        """取消实体跟随目标"""
        MDKConfig.GetModuleServer().StopCoroutine(self._trackGen)
        return self

    # -----------------------------------------------------------------------------------

    def AddParticleEntity(self, engineType, **kwargs):
        """
        添加一个特效实体\n
        - pos: tuple  默认使用创建者脚位置
        - rot: tuple  默认使用创建者转向
        - dim: int  默认使用创建者维度
        """
        if kwargs.get("forward"):
            pos = self.GetPosForward(kwargs.get("forward"))
        else:
            pos = kwargs.get("pos", self.foot_pos)
        from particle_entity import ParticleEntity
        particleEntity = ParticleEntity.Create(engineType, **{
            "pos": pos,
            "rot": kwargs.get("rot", self.rot),
            "dim": kwargs.get("dim", self.dim)
        })
        return particleEntity

    def SetCameraShake(self, targetId, intensity, seconds):
        # type: (str, float, float) -> None
        """指令的相机震动"""
        if not RawEntity.IsPlayer(targetId):
            return
        command_comp = self.comp_factory.CreateCommand(serverApi.GetLevelId())
        command_comp.SetCommand("/camerashake add @s %s %s" % (intensity, seconds), targetId)
