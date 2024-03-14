# -*- coding:utf-8 -*-


import mod.server.extraServerApi as serverApi
from ...mob.parts.entity import ModuleEntityPreset


class ModuleEffectMgr(object):
    """
    模块效果管理\n
    - 提供常用触发接口
    """
    __mVersion__ = 3
    _effect_identifier = ""  # 效果Id

    def OnRefreshEffect(self, duration, level):
        # type: (int, int) -> None
        """
        刷新效果时触发\n
        - 每次添加相同效果时触发
        - 触发时效果强度必将大于等于目前的效果强度
        """

    def OnWillAddEffect(self, duration, level):
        # type: (int, int) -> bool
        """
        即将获得相同效果\n
        - 用于控制是否添加比目前时长或等级更高的同种效果
        - 返回布尔值决定是否取消本次添加
        """
        return True

    def OnRemoveEffect(self, duration, level):
        """移除效果时触发"""

    @property
    def effect_name(self):
        # type: () -> str
        """获得效果名称"""
        return self._effect_identifier

    @classmethod
    def GetEffectName(cls):
        # type: () -> str
        """获得效果名称"""
        return cls._effect_identifier


class ModuleEffectBase(ModuleEntityPreset, ModuleEffectMgr):
    """
    模块效果基类\n
    - 使用OnSafeDestroy清除缓存引用
    """
    __mVersion__ = 2

    def __init__(self, entityId):
        super(ModuleEffectBase, self).__init__(entityId)
        self.__destroy = False
        self.effect_level = self.GetEffectLevel()
        self.effect_duration = self.GetEffectDuration()

        self.comp_factory.CreateGame(serverApi.GetPlayerList()[0]).SetNotifyMsg("init effect: %s" % self.__class__.__name__)

    def __del__(self):
        # print "[warn]", "del:%s" % self.__class__.__name__, self.id
        pass

    # -----------------------------------------------------------------------------------

    def OnSafeDestroy(self):
        """
        安全销毁\n
        - 只调用一次
        """

    def OnDestroy(self):
        # type: () -> bool
        if self.__destroy:
            return False
        self.__destroy = True
        self.OnSafeDestroy()
        super(ModuleEffectBase, self).OnDestroy()
        return True

    def OnDeath(self, killer):
        # self.EffectModule.DestroyEntityEffect(self.id, self.effect_name, id(self))
        pass

    # -----------------------------------------------------------------------------------

    def GetEffectLevel(self):
        # type: () -> int
        """获得效果等级"""
        return self.GetEffect(self.effect_name).get("amplifier", 0)

    def GetEffectDuration(self):
        # type: () -> int
        """获得效果持续时间"""
        return self.GetEffect(self.effect_name).get("duration", 0)

    def OnWillAddEffect(self, duration, level):
        pre_level = self.GetEffectLevel()
        if pre_level < level:
            return True
        elif pre_level > level:
            return False
        if self.GetEffectDuration() < duration:
            return True
        return False

    def OnRefreshEffect(self, duration, level):
        self.effect_level = level
        self.effect_duration = duration
