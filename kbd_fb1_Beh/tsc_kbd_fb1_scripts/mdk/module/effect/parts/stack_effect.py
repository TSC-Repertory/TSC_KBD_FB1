# -*- coding:utf-8 -*-


from base import ModuleEffectBase


class StackEffectBase(ModuleEffectBase):
    """堆叠效果基类"""
    __mVersion__ = 1
    _effect_identifier = "stack_effect"

    def OnSafeDestroy(self):
        super(StackEffectBase, self).OnSafeDestroy()
