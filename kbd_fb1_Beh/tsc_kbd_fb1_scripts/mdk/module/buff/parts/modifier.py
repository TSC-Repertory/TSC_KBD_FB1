# -*- coding:utf-8 -*-


from buff import *


class Modifier(Buff):
    """修改器基类"""
    __mVersion__ = 1


class StateModifier(Modifier):
    """状态修改器"""
    __mVersion__ = 1


class AttributeModifier(Modifier):
    """属性修改器"""
    __mVersion__ = 1


class MotionModifier(Modifier):
    """运动修改器"""
    __mVersion__ = 1
