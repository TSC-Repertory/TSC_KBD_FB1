# -*- coding:utf-8 -*-


from base import ModuleEffectBase


class DurationEffectBase(ModuleEffectBase):
    """
    持续效果基类\n
    - 强力效果不会缩短持续时间
    - 激活效果时不再效果累计
    """
    __mVersion__ = 2
    active_sum_time = 15  # 效果累计时间
    active_duration = 25  # 效果持续时间
    active_level = 255  # 效果触发等级

    def __init__(self, entityId):
        super(DurationEffectBase, self).__init__(entityId)
        self.ModuleSystem.RegisterUpdateSecond(self.OnUpdateSecond)
        self._sum_time = 0
        self._active_effect = False
        self._active_effect_level = 0  # 触发效果前的效果等级

    def OnSafeDestroy(self):
        self.ModuleSystem.UnRegisterUpdateSecond(self.OnUpdateSecond)

    def OnUpdateSecond(self):
        """秒更新"""
        self.effect_duration -= 1
        if not self._active_effect:
            self._sum_time += self.OnAddSumTime()
            if self._sum_time >= self.active_sum_time:
                self.OnActiveEffect()
            else:
                self.UpdateEffectSum()
        else:
            self.UpdateEffectDuration()

    def OnRefreshEffect(self, duration, level):
        if level == self.active_level:
            self._active_effect_level = self.effect_level
            self._active_effect = True
        if duration < self.effect_duration:
            self.AddEffect(self.effect_name, self.effect_duration, level)
        super(DurationEffectBase, self).OnRefreshEffect(duration, level)

    def OnWillAddEffect(self, duration, level):
        return super(DurationEffectBase, self).OnWillAddEffect(duration, level) and not self._active_effect

    def OnActiveEffect(self):
        """效果激活时触发"""
        self.AddEffect(self.effect_name, self.active_duration, self.active_level, False)

    def OnAddSumTime(self):
        # type: () -> int
        """
        添加效果积累值时触发\n
        - 可以根据效果等级和持续时间进行修正
        """
        return 1

    # -----------------------------------------------------------------------------------

    def UpdateEffectSum(self):
        """效果积累阶段循环触发"""

    def UpdateEffectDuration(self):
        """效果激活阶段循环触发"""

    # -----------------------------------------------------------------------------------

    def IsEffectActive(self):
        # type: () -> bool
        """效果是否已经激活"""
        return self._active_effect

    def GetEffectSumTime(self):
        # type: () -> int
        """获得效果累计时间"""
        return self._sum_time

    def GetActiveBeforeLevel(self):
        # type: () -> int
        """获得触发效果前的效果等级"""
        return self._active_effect_level

    # -----------------------------------------------------------------------------------

    def AddSumTime(self, value):
        # type: (int) -> None
        """增加累计时间"""
        self._sum_time = max(0, self._sum_time + value)
        if not self.IsEffectActive() and self._sum_time >= self.active_sum_time:
            self.OnActiveEffect()
