# -*- coding:utf-8 -*-


import mod.client.extraClientApi as clientApi

from raw_entity import RawEntity
from ...common.utils.misc import Misc


class Entity(object):
    """客户端实体基类"""
    __mVersion__ = 3

    def __init__(self, entityId):
        self.id = entityId
        self.comp_factory = clientApi.GetEngineCompFactory()
        self.type_str = self.comp_factory.CreateEngineType(self.id).GetEngineTypeStr()
        self.query_comp = self.comp_factory.CreateQueryVariable(self.id)
        self.game_comp = self.comp_factory.CreateGame(self.id)
        self.attr_comp = self.comp_factory.CreateAttr(self.id)
        self.rot_comp = self.comp_factory.CreateRot(self.id)
        self.pos_comp = self.comp_factory.CreatePos(self.id)

    # -----------------------------------------------------------------------------------

    @property
    def foot_pos(self):
        return self.GetPos()

    @property
    def rot(self):
        return self.GetRot()

    @property
    def drt(self):
        return self.GetDrt()

    # -----------------------------------------------------------------------------------

    def IsAlive(self):
        # type: () -> bool
        """实体是否存活"""
        return self.game_comp.IsEntityAlive(self.id)

    def IsOnGround(self):
        """
        检测玩家是否触地\n
        客户端实体刚创建时引擎计算还没完成，此时获取该实体是否着地将返回默认值True，需要延迟一帧进行获取才能获取到正确的数据\n
        - 生物处于骑乘状态时，如玩家骑在猪身上，也视作触地\n
        - 只能获取到本地客户端已加载的实体是否触地
        - 若实体在其他维度或未加载（距离本地玩家太远），将获取失败
        """
        return self.attr_comp.isEntityOnGround()

    def IsInLava(self):
        """
        实体是否在岩浆中\n
        - 只能获取到本地客户端已加载的实体是否在岩浆中
        - 若实体在其他维度或未加载（距离本地玩家太远），将获取失败
        """
        return self.attr_comp.isEntityInLava()

    def IsPlayer(self):
        # type: () -> bool
        """是否为玩家"""
        return self.type_str == "minecraft:player"

    # -----------------------------------------------------------------------------------

    def GetPos(self, onEye=False):
        # type: (bool) -> tuple
        """获取实体坐标"""
        if not onEye:
            return self.pos_comp.GetFootPos()
        return self.pos_comp.GetPos()

    def GetRot(self):
        # type: () -> tuple
        """获取实体转角"""
        return self.rot_comp.GetRot()

    def SetRot(self, rot):
        # type: (tuple) -> None
        """设置实体转角"""
        self.rot_comp.SetRot(rot)

    def GetBodyRot(self):
        # type: () -> float
        """获得身体朝向"""
        return self.rot_comp.GetBodyRot()

    def GetDrt(self, horizon=False):
        """获取实体朝向的单位坐标"""
        rot = self.GetRot()
        if not horizon:
            return clientApi.GetDirFromRot(rot)
        return clientApi.GetDirFromRot((0, rot[1]))

    def GetScale(self):
        # type: () -> float
        """获取实体模型大小"""
        return self.query_comp.GetMolangValue("query.model_scale") * 16

    # -----------------------------------------------------------------------------------

    def GetPosForward(self, n, height=0.0):
        """获取实体前方的位置"""
        drt = self.GetDrt()
        pos = self.GetPos()
        atPos = tuple(map(lambda x, y, z: x + y * z, pos, drt, [n, 0, n]))
        if not height:
            return atPos
        return Misc.GetPosModify(atPos, (0, height, 0))

    def GetMobInRadius(self, radius):
        # type: (int) -> list
        """获得范围生物"""
        pos = self.foot_pos
        start = Misc.GetPosModify(pos, (-radius,) * 3)
        end = Misc.GetPosModify(pos, (radius,) * 3)
        return self.game_comp.GetEntityInArea(self.id, start, end)

    # -----------------------------------------------------------------------------------

    def SetShowName(self, visible):
        # type: (bool) -> bool
        """设置名字显示"""
        return self.comp_factory.CreateName(self.id).SetShowName(visible)

    def SetAlwaysShowName(self, visible):
        # type: (bool) -> bool
        """设置名字常显示"""
        return self.comp_factory.CreateName(self.id).SetAlwaysShowName(visible)

    def GetChName(self):
        # type: () -> str
        """获得实体中文名称"""
        return RawEntity.GetChNameByType(self.type_str)
