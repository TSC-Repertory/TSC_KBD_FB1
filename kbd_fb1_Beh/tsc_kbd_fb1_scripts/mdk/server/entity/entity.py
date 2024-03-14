# -*- coding:utf-8 -*-


import math

from mod.common.utils.mcmath import Vector3

from raw_entity import RawEntity
from ...common.system.base import *
from ...common.utils.misc import Misc
from ...server.item.base import ServerItem


class Entity(object):
    """服务端实体基类"""
    __mVersion__ = 9

    def __init__(self, entityId):
        self.id = entityId
        self.comp_factory = serverApi.GetEngineCompFactory()
        self.game_comp = self.comp_factory.CreateGame(serverApi.GetLevelId())
        self.attr_comp = self.comp_factory.CreateAttr(self.id)

        # 暂存数据
        self.dataTemp = 0
        self.dataList = []
        self.dataDict = {}

    # -----------------------------------------------------------------------------------

    @property
    def type_str(self):
        # type: () -> str
        """获取实体的类型名称"""
        return self.comp_factory.CreateEngineType(self.id).GetEngineTypeStr()

    @property
    def foot_pos(self):
        return RawEntity.GetPos(self.id, False)

    @property
    def eye_pos(self):
        return RawEntity.GetPos(self.id, True)

    @property
    def rot(self):
        return self.GetRot()

    @property
    def drt(self):
        return self.GetDrt()

    @property
    def dim(self):
        # type: () -> int
        """获得实体维度"""
        return RawEntity.GetDim(self.id)

    # -----------------------------------------------------------------------------------

    def Kill(self):
        """使用杀死的方式清除实体"""
        self.game_comp.KillEntity(self.id)

    def Destroy(self, delay=0.0):
        # type: (float) -> Entity
        """清除实体"""
        if delay > 0:
            self.SetPersistent(False)
            self.game_comp.AddTimer(delay, self._Destroy)
        else:
            self._Destroy()
        return self

    def _Destroy(self):
        system = MDKConfig.GetModuleServer()
        system.DestroyEntity(self.id)

    # -----------------------------------------------------------------------------------

    def IsAlive(self):
        # type: () -> bool
        """实体是否存活"""
        return RawEntity.IsAlive(self.id)

    def IsMob(self):
        # type: () -> bool
        """判断实体是否是生物"""
        return RawEntity.IsMob(self.id)

    def IsPlayer(self):
        # type: () -> bool
        """判断实体是否是玩家"""
        return self.GetType() & minecraftEnum.EntityType.Player == minecraftEnum.EntityType.Player

    def IsProjectile(self):
        # type: () -> bool
        """判断实体是否是抛射物"""
        return self.GetType() & minecraftEnum.EntityType.Projectile == minecraftEnum.EntityType.Projectile

    def IsSameTypeWith(self, entityId):
        # type: (str) -> bool
        """
        判断是否和自己有相同的family\n
        - other: str 生物Id
        """
        target = set(self.GetFamily())
        other = set(RawEntity.GetFamily(entityId))
        return target & other == target

    def IsOnFire(self):
        # type: () -> bool
        """实体是否着火"""
        return self.attr_comp.IsEntityOnFire()

    # -----------------------------------------------------------------------------------

    def GetPos(self, onEye=False, dx=0.0, dy=0.0):
        """获取实体位置"""
        atPos = RawEntity.GetPos(self.id, onEye)
        if dx != 0.0:
            atRot = self.GetRot(dx=90)
            atDrt = serverApi.GetDirFromRot(atRot)
            atPos = Misc.GetPosModify(atPos, (atDrt[0] * dx, dy, atDrt[2] * dx))
        elif dy != 0.0:
            atPos = Misc.GetPosModify(atPos, (0, dy, 0))
        return atPos

    def SetPos(self, pos, onFoot=True):
        # type: (tuple, bool) -> Entity
        """设置实体位置"""
        posComp = self.comp_factory.CreatePos(self.id)
        posComp.SetFootPos(pos) if onFoot else posComp.SetPos(pos)
        return self

    def SetRelativePos(self, dx=0.0, dy=0.0, dz=0.0):
        # type: (float, float, float) -> Entity
        """设置相对位置"""
        atPos = Misc.GetPosModify(self.foot_pos, (dx, dy, dz))
        self.SetPos(atPos)
        return self

    def GetPosForwardVec(self, n, **kwargs):
        # type: (float, any) -> Vector3
        """获得实体前方n格的向量"""
        rot = self.GetRot(kwargs.get("horizon", True))
        return Vector3(serverApi.GetDirFromRot((0, rot[1]))) * n

    def GetPosForward(self, n, **kwargs):
        """
        获取实体前方n格位置\n
        可传参数:\n
        - onEye: bool是否从眼睛位置出发 对非玩家无效
        - horizon: bool是否水平朝向
        :param n: float前方格数
        :return: tuple前方的位置
        """
        atPos = self.GetPos(kwargs.get("onEye", False), dx=kwargs.get("dx", 0.0), dy=kwargs.get("dy", 0.0))
        atRot = self.GetRot(kwargs.get("horizon", True))
        atDrt = serverApi.GetDirFromRot((0, atRot[1]))
        return tuple(map(lambda x, y, z: x + y * z, atPos, atDrt, [n, 0, n]))

    def GetPosHeng(self, rot, n, **kwargs):
        atPos = self.GetPos()
        atRot = rot
        atDrt = serverApi.GetDirFromRot((0, atRot[1]))
        return tuple(map(lambda x, y, z: x + y * z, atPos, atDrt, [n, 0, n]))

    def SetPosForward(self, n, **kwargs):
        # type: (float, any) -> Entity
        """
        获取实体前方n格位置\n
        - n: float前方格数
        可传参数:\n
        - onEye: bool是否从眼睛位置出发 对非玩家无效
        - horizon: bool是否水平朝向
        """
        atPos = self.GetPosForward(n, **kwargs)
        self.SetPos(atPos)
        return self

    def GetModifyPos(self, onEye=False, dx=0.0, dy=0.0, dz=0.0, lock_y=0.0):
        """获取实体位置"""
        atPos = RawEntity.GetPos(self.id, onEye)
        if dx != 0.0:
            atRot = self.GetRot(dx=90)
            atDrt = serverApi.GetDirFromRot(atRot)
            atPos = Misc.GetPosModify(atPos, (atDrt[0] * dx, 0, atDrt[2] * dx))
        if dz != 0.0:
            atRot = self.GetRot()
            atDrt = serverApi.GetDirFromRot(atRot)
            atPos = Misc.GetPosModify(atPos, (atDrt[0] * dz, 0, atDrt[2] * dz))
        if dy != 0.0:
            atPos = Misc.GetPosModify(atPos, (0, dy, 0))
        if lock_y != 0.0:
            atPos = (atPos[0], lock_y, atPos[2])
        return atPos

    def GetRadiusPosForward(self, n, radius, **kwargs):
        """获取实体前方一定半径的圆周点竖直排布"""
        posList = []
        atPos = kwargs.get("atPos", self.GetPos())
        atRot = kwargs.get("atRot", self.GetRot(horizon=True))
        forward = kwargs.get("forward", 0)
        height = kwargs.get("height", 0)
        atDrt = serverApi.GetDirFromRot(atRot)
        for degree in xrange(0, 360, 360 // n):
            theta = math.radians(degree)
            dx = radius * math.cos(theta)
            dz = radius * math.sin(theta)
            x = atPos[0] + dx * math.cos(math.radians(atRot[1])) + atDrt[0] * forward
            y = atPos[1] + dz + height
            z = atPos[2] + dx * math.sin(math.radians(atRot[1])) + atDrt[2] * forward
            posList.append((x, y, z))
        return posList

    # -----------------------------------------------------------------------------------

    def GetRot(self, horizon=False, dx=0.0, dy=0.0):
        # type: (bool, float, float) -> tuple
        """获取实体转向"""
        atRot = RawEntity.GetRot(self.id, horizon)
        if dx or dy:
            atRot = Misc.GetPosModify(atRot, (dy, dx))
        return atRot

    def GetOppositeRot(self, horizon=False):
        # type: (bool) -> tuple
        """获得转向相反"""
        atRot = RawEntity.GetRot(self.id, horizon)
        return Misc.GetPosModify(atRot, (-1, 1), method="multi")

    def SetRot(self, rot):
        # type: (tuple) -> Entity
        """设置实体转向"""
        self.comp_factory.CreateRot(self.id).SetRot(rot)
        return self

    def SetRelativeRot(self, dx=0.0, dy=0.0):
        # type: (float, float) -> Entity
        """设置相对位置"""
        atRot = Misc.GetPosModify(self.rot, (dy, dx))
        self.SetRot(atRot)
        return self

    # -----------------------------------------------------------------------------------

    def GetDrt(self, horizon=False):
        # type: (bool) -> tuple
        """获取实体通过旋转角度获取的朝向"""
        return RawEntity.GetDrt(self.id, horizon)

    def GetType(self):
        # type: () -> int
        """获得生物类型"""
        return self.comp_factory.CreateEngineType(self.id).GetEngineType()

    def GetFamily(self):
        # type: () -> [str]
        """获取生物行为包字段 type_family"""
        return RawEntity.GetFamily(self.id)

    # -----------------------------------------------------------------------------------

    def SetPersistent(self, persistence=False):
        """
        设置实体是否存盘\n
        默认不存盘\n
        游戏中，实体默认持久化，若设置不持久化，则实体会在区块卸载和退出存档时被删除，不会存档
        """
        self.comp_factory.CreatePersistence(self.id).SetPersistence(persistence)
        return self

    def SetImmuneDamage(self, immune=True):
        # type: (bool) -> Entity
        """设置实体免疫伤害"""
        self.comp_factory.CreateHurt(self.id).ImmuneDamage(immune)
        return self

    def SetHurtVisible(self, visible):
        # type: (bool) -> Entity
        """设置骨骼模型是否显示伤害变红"""
        model_comp = self.comp_factory.CreateModel(self.id)
        model_comp.ShowCommonHurtColor(visible)
        return self

    # -----------------------------------------------------------------------------------

    def GetName(self):
        # type: () -> str
        """获取生物定义名字"""
        return RawEntity.GetName(self.id)

    def GetRealName(self):
        return RawEntity.GetEngineTypeName(self.type_str)

    def SetName(self, name):
        # type: (str) -> Entity
        """设置名称"""
        self.comp_factory.CreateName(self.id).SetName(name)
        return self

    # -----------------------------------------------------------------------------------

    def GetCollisionBoxSize(self):
        # type: () -> [float, float]
        """获取实体的包围盒"""
        return self.comp_factory.CreateCollisionBox(self.id).GetSize()

    def SetCollisionBoxSize(self, size):
        # type: (tuple) -> bool
        """
        设置实体的包围盒\n
        对新生产的实体需要经过5帧之后再设置包围盒的大小才会生效
        """
        return self.comp_factory.CreateCollisionBox(self.id).SetSize(size)

    # -----------------------------------------------------------------------------------

    def GetGravity(self):
        # type: () -> float
        """
        获取实体的重力因子，\n
        当生物重力因子为0时则应用世界的重力因子
        """
        return self.comp_factory.CreateGravity(self.id).GetGravity()

    def SetGravity(self, value):
        # type: (float) -> bool
        """
        设置实体的重力因子，\n
        当生物重力因子为0时则应用世界的重力因子
        """
        return self.comp_factory.CreateGravity(self.id).SetGravity(value)

    # -----------------------------------------------------------------------------------

    def SetModel(self, model):
        # type: (str) -> Entity
        """设置模型"""
        model_comp = self.comp_factory.CreateModel(self.id)
        model_comp.SetModel(model)
        return self

    def SetScale(self, scale):
        # type: (float) -> Entity
        """设置实体尺寸"""
        self.comp_factory.CreateScale(self.id).SetEntityScale(self.id, scale)
        return self

    # -----------------------------------------------------------------------------------

    def GetMobInRadius(self, radius, **kwargs):
        """
        获取一定半径的生物\n
        可传参数：\n
        - detector: str 检测体Id
        - filters: GameFilter 过滤器
        :param radius: int 方形范围半径
        :return: list 生物列表
        """
        detector = kwargs.get("detector", self.id)
        filters = kwargs.get("filters", GameFilter.Mob)
        banList = kwargs.get("banList", [self.id])
        resList = self.game_comp.GetEntitiesAround(detector, radius, filters)
        if banList:
            resSet = set(resList)
            resSet.difference_update(set(banList))
            return list(resSet)
        return resList

    def GetMobAtPos(self, atPos, radius, **kwargs):
        """获取某点的半径生物"""
        kwargs.get("filters")
        if kwargs.get("forward"):
            atPos = self.GetPosForward(kwargs.get("forward"))
        markEntity = RawEntity.Create(GameEntity.detector, pos=atPos, dim=self.dim)
        resList = self.GetMobInRadius(radius, detector=markEntity.id, **kwargs)
        markEntity.Destroy()
        banList = kwargs.get("banList", [])
        banList.append(markEntity.id)
        resSet = set(resList)
        resSet.difference_update(set(banList))
        return list(resSet)

    def GetSectorEntity(self, radius, angle, backward=0, **kwargs):
        # type: (int, any, float, any) -> list
        """
        获得扇形区域实体列表\n
        - radius: int
        - angle:
            - tuple (min_val, max_val)
            - float -> (-angle, angle)
        - backward: float
        """
        res = []
        from_rot = self.rot
        vec_pos = Vector3(self.foot_pos)
        entities = self.game_comp.GetEntitiesAround(self.id, radius, GameFilter.Mob)
        if backward:
            vec_pos += Vector3(self.GetPosForwardVec(backward))
        if not isinstance(angle, tuple):
            angle = abs(angle)
            angle = (-angle, angle)
        banList = kwargs.get("banList", [self.id])
        for entityId in entities:
            if entityId in banList:
                continue
            entityPos = RawEntity.GetPos(entityId)
            if entityPos:
                face_rot = serverApi.GetRotFromDir((vec_pos - Vector3(entityPos)).ToTuple())
                check_angle = abs(from_rot[1] - face_rot[1]) - 180
                if angle[0] < check_angle < angle[1]:
                    res.append(entityId)
        return res

    # -----------------------------------------------------------------------------------

    def SetMotion(self, motion):
        # type: (tuple) -> Entity
        """设置实体动量"""
        self.comp_factory.CreateActorMotion(self.id).SetMotion(motion)
        return self

    # -----------------------------------------------------------------------------------

    def AddTag(self, tag):
        # type: (str) -> bool
        """增加实体标签"""
        return self.comp_factory.CreateTag(self.id).AddEntityTag(tag)

    def GetTag(self):
        # type: () -> list
        """获取实体标签列表"""
        return self.comp_factory.CreateTag(self.id).GetEntityTags()

    def HasTag(self, tag):
        # type: (str) -> bool
        """判断实体是否存在某个指定的标签"""
        return self.comp_factory.CreateTag(self.id).EntityHasTag(tag)

    def RemoveTag(self, tag):
        # type: (str) -> bool
        """移除实体某个指定的标签"""
        return self.comp_factory.CreateTag(self.id).RemoveEntityTag(tag)

    # -----------------------------------------------------------------------------------

    def asSkillEntity(self):
        """将实例转成SkillEntity"""
        from skill_entity import SkillEntity
        return SkillEntity(self.id)

    def asLivingEntity(self):
        """将实例转成LivingEntity"""
        from living_entity import LivingEntity
        return LivingEntity(self.id)

    def asParticleEntity(self):
        """将实例转成ParticleEntity"""
        from particle_entity import ParticleEntity
        return ParticleEntity(self.id)

    # -----------------------------------------------------------------------------------

    def ChangeDimension(self, dimId, pos):
        # type: (int, tuple) -> None
        """传送实体"""
        comp = self.comp_factory.CreateDimension(self.id)
        if comp.GetEntityDimensionId() == dimId:
            self.SetPos(pos)
        else:
            comp.ChangePlayerDimension(dimId, pos) if self.IsPlayer() else comp.ChangeEntityDimension(dimId, pos)

    def SpawnItem(self, item, **kwargs):
        # type: (any, any) -> bool
        """生成物品"""
        if isinstance(item, str):
            item = ServerItem.Create(item, **kwargs)
        if not isinstance(item, dict):
            return False
        item_comp = self.comp_factory.CreateItem(self.id)
        return item_comp.SpawnItemToLevel(item, self.dim, kwargs.get("pos", self.foot_pos))

    def SpawnItemToEntity(self, entityId, itemDict, **kwargs):
        # type: (str, dict, any) -> bool
        """生成物品到实体"""
        item_comp = self.comp_factory.CreateItem(self.id)
        spawn_pos = kwargs.get("pos", RawEntity.GetPos(entityId))
        dim = kwargs.get("dim", RawEntity.GetDim(entityId))
        return item_comp.SpawnItemToLevel(itemDict, dim, spawn_pos)

    # -----------------------------------------------------------------------------------

    def PlayAnimation(self, animKey):
        # type: (str) -> None
        """指令播放动画"""
        command_comp = self.comp_factory.CreateCommand(serverApi.GetLevelId())
        command_comp.SetCommand("/playanimation @s %s" % animKey, self.id)

    # -----------------------------------------------------------------------------------

    def TriggerCustomEvent(self, eventName):
        # type: (str) -> None
        """触发生物自定义事件"""
        if self.IsAlive():
            self.comp_factory.CreateEntityEvent(self.id).TriggerCustomEvent(self.id, eventName)

    # -----------------------------------------------------------------------------------

    def CanSeeTarget(self, targetId, **kwargs):
        """
        判断起始对象是否可看见目标对象,基于对象的Head位置判断\n
        - targetId: str 目标对象ID
        - viewRange: float 视野距离,默认值8.0
        - onlySolid: bool 只判断固体方块遮挡,默认True; False则液体方块也会遮挡
        - angleX: float 视野X轴角度,默认值180.0度
        - angleY: float 视野Y轴角度,默认值180.0度
        """
        viewRange = kwargs.get("viewRange", 8.0)
        onlySolid = kwargs.get("onlySolid", True)
        angleX = kwargs.get("angleX", 180.0)
        angleY = kwargs.get("angleY", 180.0)
        return self.game_comp.CanSee(self.id, targetId, viewRange, onlySolid, angleX, angleY)

    # -----------------------------------------------------------------------------------

    def GetFacingVec(self, pos):
        # type: (tuple) -> tuple
        """获得朝向目标的向量"""
        try:
            vector = Vector3(pos)
            vector -= Vector3(self.foot_pos)
            vector = vector.Normalized()  # type: Vector3
            return vector.ToTuple()
        except ValueError:
            print "[info]", "输入参数错误：", pos
            return 0, 0, 0

    def GetFacingEntityVec(self, target_id):
        # type: (str) -> tuple
        """
        获得对准目标的单位向量\n
        常用于motion操作
        """
        return self.GetFacingVec(RawEntity.GetPos(target_id))

    def SetFacingEntity(self, targetId):
        # type: (str) -> bool
        """设置朝向目标实体"""
        drt = self.GetFacingEntityVec(targetId)
        # if not all(drt):
        #     return False
        self.SetRot(serverApi.GetRotFromDir(drt))
        return True

    def SetFacingPos(self, pos):
        # type: (tuple) -> None
        """设置朝向目标位置"""
        drt = self.GetFacingVec(pos)
        self.SetRot(serverApi.GetRotFromDir(drt))

    def GetDistanceWith(self, entityId):
        """获得与实体的距离"""
        if entityId == self.id or not RawEntity.IsAlive(entityId):
            return 0
        return Misc.GetDistBetween(self.foot_pos, RawEntity.GetPos(entityId))

    # -----------------------------------------------------------------------------------

    """仇恨目标相关"""

    def GetAttackTarget(self):
        # type: () -> str
        """获得仇恨目标"""
        target_id = self.comp_factory.CreateAction(self.id).GetAttackTarget()
        if target_id == "-1":
            target_id = ""
        return target_id

    def SetAttackTarget(self, targetId):
        # type: (str) -> bool
        """设置仇恨目标"""
        return self.comp_factory.CreateAction(self.id).SetAttackTarget(targetId)

    def ResetAttackTarget(self):
        # type: () -> bool
        """清除仇恨目标"""
        return self.comp_factory.CreateAction(self.id).ResetAttackTarget()

    # -----------------------------------------------------------------------------------

    """战利品相关"""

    def SpawnLoot(self, pos=None):
        """
        生成该生物的战利品\n
        - 创建战利品工厂需要玩家id
        - 生成时实体需要存活
        """
        if not pos:
            pos = tuple(map(int, self.foot_pos))
        self.comp_factory.CreateActorLoot(serverApi.GetPlayerList()[0]).SpawnLootTableWithActor(pos, self.id)
