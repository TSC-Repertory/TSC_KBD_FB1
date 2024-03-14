# -*- coding:utf-8 -*-


from mod.common.minecraftEnum import EntityType, AttrType
from mod.common.utils.mcmath import Vector3

from ...common.system.base import *
from ...common.utils.misc import Misc


class RawEntity(object):
    """服务端生物方法"""
    __mVersion__ = 7

    @classmethod
    def Create(cls, engineType, **kwargs):
        """创建实体实例"""
        entityId = cls.CreateRaw(engineType, **kwargs)
        if not entityId:
            return
        from living_entity import LivingEntity
        return LivingEntity(entityId)

    @staticmethod
    def CreateRaw(engineType, pos, dim, rot=(0, 0)):
        """创建实体实例"""
        system = MDKConfig.GetModuleServer()
        entityId = system.CreateEngineEntityByTypeStr(engineType, pos, rot, dim)
        if not entityId:
            print "[warn]", "创建实体失败：", engineType
            return
        return entityId

    @classmethod
    def GetType(cls, entityId):
        # type: (str) -> int
        """获得实体类型"""
        engine_comp = serverApi.GetEngineCompFactory().CreateEngineType(entityId)
        return engine_comp.GetEngineType()

    @classmethod
    def GetTypeStr(cls, entityId):
        # type: (str) -> str
        """获取实体Id类型"""
        engine_comp = serverApi.GetEngineCompFactory().CreateEngineType(entityId)
        return engine_comp.GetEngineTypeStr()

    @classmethod
    def GetPos(cls, entityId, onEye=False):
        # type: (str, bool) -> tuple
        """获取实体位置"""
        pos_comp = serverApi.GetEngineCompFactory().CreatePos(entityId)
        return pos_comp.GetPos() if onEye else pos_comp.GetFootPos()

    @classmethod
    def GetCollisionPos(cls, entityId, dy=0, ry=0):
        # type: (str, float, float) -> tuple
        """获得实体碰撞箱相对位置"""
        box_comp = serverApi.GetEngineCompFactory().CreateCollisionBox(entityId)
        size = box_comp.GetSize()
        pos = cls.GetPos(entityId)
        if dy:
            return Misc.GetPosModify(pos, (0, dy, 0))
        elif ry:
            return Misc.GetPosModify(pos, (0, size[1] * ry, 0))
        return pos

    @classmethod
    def SetPos(cls, entityId, atPos):
        # type: (str, tuple) -> bool
        """获取实体位置"""
        pos_comp = serverApi.GetEngineCompFactory().CreatePos(entityId)
        return pos_comp.SetPos(atPos)

    @classmethod
    def GetModifyPos(cls, entityId, offset, pos=None):
        """获取实体位置"""
        dx, dy, dz = offset
        if not pos:
            pos = RawEntity.GetPos(entityId)
        if dx != 0.0:
            drt = serverApi.GetDirFromRot(cls.GetEntityRotModify(entityId, dx=90))
            if not drt:
                drt = [0, 0, 0]
            pos = Misc.GetPosModify(pos, (drt[0] * dx, 0, drt[2] * dx))
        if dz != 0.0:
            drt = serverApi.GetDirFromRot(cls.GetRot(entityId))
            if not drt:
                drt = [0, 0, 0]
            pos = Misc.GetPosModify(pos, (drt[0] * dz, 0, drt[2] * dz))
        if dy != 0.0:
            pos = Misc.GetPosModify(pos, (0, dy, 0))
        return pos

    @classmethod
    def SetRot(cls, targetId, rot):
        # type: (str, tuple) -> bool
        """设置实体转向"""
        rot_comp = serverApi.GetEngineCompFactory().CreateRot(targetId)
        return rot_comp.SetRot(rot)

    @classmethod
    def GetRot(cls, entityId, horizon=False):
        # type: (str, bool) -> tuple
        """获取实体转向"""
        rot_comp = serverApi.GetEngineCompFactory().CreateRot(entityId)
        rot = rot_comp.GetRot()
        if horizon:
            rot = (0, rot[1])
        return rot

    @classmethod
    def GetEntityRotModify(cls, entityId, horizon=False, dx=0.0, dy=0.0):
        # type: (str ,bool, float, float) -> tuple
        """获取实体转向修正"""
        rot = RawEntity.GetRot(entityId, horizon)
        if dx or dy:
            rot = Misc.GetPosModify(rot, (dy, dx))
        return rot

    @classmethod
    def GetDrt(cls, entityId, horizon=False):
        # type: (str, bool) -> tuple
        """获取实体通过旋转角度获取的朝向"""
        atRot = cls.GetRot(entityId, horizon)
        return serverApi.GetDirFromRot(atRot)

    @classmethod
    def GetFacingPosVec(cls, entityId, pos):
        # type: (str, tuple) -> tuple
        """获得朝向目标的向量"""
        try:
            vector = Vector3(pos)
            vector -= Vector3(RawEntity.GetPos(entityId))
            vector = vector.Normalized()  # type: Vector3
            return vector.ToTuple()
        except ValueError:
            print "[info]", "输入参数错误：", pos
            return 0, 0, 0

    @classmethod
    def GetFacingEntityVec(cls, entityId, targetId):
        # type: (str, str) -> tuple
        """获得实体朝向另一个实体的向量"""
        target_pos = cls.GetPos(targetId)
        return cls.GetFacingPosVec(entityId, target_pos)

    @classmethod
    def GetDim(cls, entityId):
        # type: (str) -> int
        """获取实体维度Id"""
        dim_comp = serverApi.GetEngineCompFactory().CreateDimension(entityId)
        return dim_comp.GetEntityDimensionId()

    @classmethod
    def GetName(cls, entityId):
        # type: (str) -> str
        """
        获取名称\n
        - 优先获取命名牌设置的名称
        """
        name_comp = serverApi.GetEngineCompFactory().CreateName(entityId)
        name = name_comp.GetName()
        if name:
            return name
        return cls.GetEngineTypeName(cls.GetTypeStr(entityId))

    @classmethod
    def GetEngineTypeName(cls, engine_type):
        # type: (str) ->  str
        """获得生物类型名字"""
        if not engine_type:
            return ""
        game_comp = serverApi.GetEngineCompFactory().CreateGame(serverApi.GetLevelId())
        name_key = "entity.%s.name" % engine_type.replace("minecraft:", "")
        return game_comp.GetChinese(name_key).encode("utf-8")

    @classmethod
    def GetFamily(cls, entityId):
        # type: (str) -> list
        attr_comp = serverApi.GetEngineCompFactory().CreateAttr(entityId)
        family = attr_comp.GetTypeFamily()
        return family if isinstance(family, list) else []

    @classmethod
    def AddEffect(cls, entityId, effectName, duration=10, amplifier=0, showParticles=True):
        # type: (str, str, int, int, bool) -> bool
        """设置实体药水效果"""
        effect_comp = serverApi.GetEngineCompFactory().CreateEffect(entityId)
        return effect_comp.AddEffectToEntity(effectName, duration, amplifier, showParticles)

    @classmethod
    def IsMob(cls, entityId):
        # type: (str) -> bool
        """判断是否是生物"""
        return cls.GetType(entityId) & EntityType.Mob == EntityType.Mob

    @classmethod
    def IsItem(cls, entityId):
        # type: (str) -> bool
        """判断是否是物品"""
        return cls.GetType(entityId) & EntityType.ItemEntity == EntityType.ItemEntity

    @classmethod
    def IsAlive(cls, entityId):
        # type: (str) -> bool
        """实体是否存活"""
        game_comp = serverApi.GetEngineCompFactory().CreateGame(serverApi.GetLevelId())
        return game_comp.IsEntityAlive(entityId)

    @classmethod
    def IsPlayer(cls, entityId):
        # type: (str) -> bool
        """实体是否是玩家"""
        return cls.GetTypeStr(entityId) == "minecraft:player"

    @classmethod
    def IsMinecraftEntity(cls, entityId):
        # type: (str) -> bool
        """是否为原版实体"""
        return cls.GetTypeStr(entityId).startswith("minecraft:")

    @classmethod
    def GetInfoForProjectile(cls, entityId, horizon=True):
        # type: (str, bool) -> dict
        """
        获取实体的信息\n
        常用于创建抛射物构建\n
        默认使用实体的位置和朝向
        """
        return {"position": cls.GetPos(entityId, True), "direction": cls.GetDrt(entityId, horizon)}

    @classmethod
    def GetDataComp(cls, entityId):
        """获得实体数据组件"""
        return serverApi.GetEngineCompFactory().CreateExtraData(entityId)

    @classmethod
    def AddTag(cls, entityId, tag):
        # type: (str, str) -> bool
        """增加实体标签"""
        tag_comp = serverApi.GetEngineCompFactory().CreateTag(entityId)
        return tag_comp.AddEntityTag(tag)

    @classmethod
    def HasTag(cls, entityId, tag):
        # type: (str, any) -> bool
        """是否有实体标签"""
        if isinstance(tag, str):
            tag = [tag]
        tag = set(tag)
        tags = set(serverApi.GetEngineCompFactory().CreateTag(entityId).GetEntityTags())
        return tag & tags == tag

    @classmethod
    def RunCommand(cls, command):
        # type: (str) -> None
        """运行指令"""
        command_comp = serverApi.GetEngineCompFactory().CreateCommand(serverApi.GetLevelId())
        command_comp.SetCommand(command, serverApi.GetPlayerList()[0])

    @classmethod
    def PlaySound(cls, name, pos):
        # type: (str, tuple) -> None
        """播放声音"""
        command = "/playsound {} @a {} {} {} 1 1".format(name, *pos)
        cls.RunCommand(command)

    @classmethod
    def GetHealth(cls, entityId):
        # type: (str) -> float
        """获得实体生命值"""
        attr_comp = serverApi.GetEngineCompFactory().CreateAttr(entityId)
        return attr_comp.GetAttrValue(AttrType.HEALTH)
