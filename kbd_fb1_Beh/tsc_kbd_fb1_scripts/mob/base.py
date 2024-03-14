# -*- coding:utf-8 -*-

from ..mdk.common.system import *
from ..mdk.module.mob.parts.entity import ModuleEntityPreset


class ModEntityBase(ModuleEntityPreset):
    """模组生物基类"""

    def __init__(self, entityId):
        super(ModEntityBase, self).__init__(entityId)

