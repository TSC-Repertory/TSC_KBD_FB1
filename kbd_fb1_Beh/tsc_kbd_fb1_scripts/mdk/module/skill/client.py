# -*- coding:utf-8 -*-


from const import *
from parser import SkillParser
from ...module.system.base import *


class SkillModuleClient(ModuleClientBase):
    """技能模块客户端"""
    __mVersion__ = 1
    __identifier__ = ModuleEnum.identifier

    def __init__(self):
        super(SkillModuleClient, self).__init__()
        self.ModuleSystem.SetModConfigParser(SkillParser())
