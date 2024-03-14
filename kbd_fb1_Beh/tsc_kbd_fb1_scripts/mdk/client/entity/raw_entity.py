# -*- coding:utf-8 -*-


import mod.client.extraClientApi as clientApi
from mod.common.minecraftEnum import EntityType


class RawEntity(object):
    """生物基类方法"""
    __mVersion__ = 5

    @classmethod
    def GetPos(cls, entityId, onEye=False):
        # type: (str, bool) -> tuple
        """获取实体坐标"""
        comp_factory = clientApi.GetEngineCompFactory()
        pos_comp = comp_factory.CreatePos(entityId)
        if not onEye:
            return pos_comp.GetFootPos()
        return pos_comp.GetPos()

    @classmethod
    def GetRot(cls, entityId):
        # type: (str) -> tuple
        """获取实体转角"""
        comp_factory = clientApi.GetEngineCompFactory()
        return comp_factory.CreateRot(entityId).GetRot()

    @classmethod
    def GetDrt(cls, entityId, horizon=False):
        # type: (str, bool) -> tuple
        """获取实体朝向的单位坐标"""
        rot = cls.GetRot(entityId)
        if horizon:
            return clientApi.GetDirFromRot((0, rot[1]))
        return clientApi.GetDirFromRot(rot)

    @classmethod
    def GetScale(cls, entityId):
        # type: (str) -> float
        """获取实体模型大小"""
        comp_factory = clientApi.GetEngineCompFactory()
        scale = comp_factory.CreateQueryVariable(entityId).GetMolangValue("query.model_scale")
        return scale * 16

    @classmethod
    def GetTypeStr(cls, entityId):
        # type: (str) -> str
        """获取实体的类型名称"""
        comp_factory = clientApi.GetEngineCompFactory()
        return comp_factory.CreateEngineType(entityId).GetEngineTypeStr()

    @classmethod
    def GetType(cls, entityId):
        # type: (str) -> int
        """获得实体类型"""
        comp_factory = clientApi.GetEngineCompFactory()
        return comp_factory.CreateEngineType(entityId).GetEngineType()

    @classmethod
    def GetChName(cls, entityId):
        # type: (str) -> str
        """获得实体中文名称"""
        type_str = cls.GetTypeStr(entityId)
        return cls.GetChNameByType(type_str)

    @classmethod
    def GetChNameByType(cls, type_str):
        # type: (str) -> str
        """获得实体中文名称"""
        name_key = "entity.%s.name" % type_str.replace("minecraft:", "")
        comp_factory = clientApi.GetEngineCompFactory()
        return comp_factory.CreateGame(clientApi.GetLevelId()).GetChinese(name_key)

    @classmethod
    def IsMob(cls, entityId):
        # type: (str) -> bool
        """判断是否是生物"""
        return cls.GetType(entityId) & EntityType.Mob == EntityType.Mob

    @classmethod
    def IsPlayer(cls, entity_id):
        # type: (str) -> bool
        """判断是否是玩家"""
        return cls.GetType(entity_id) & EntityType.Player == EntityType.Player

    @classmethod
    def GetMaxHealth(cls, entityId):
        # type: (str) -> float
        """获得实体最大生命值"""
        comp_factory = clientApi.GetEngineCompFactory()
        query_comp = comp_factory.CreateQueryVariable(entityId)
        return query_comp.GetMolangValue("query.max_health")
