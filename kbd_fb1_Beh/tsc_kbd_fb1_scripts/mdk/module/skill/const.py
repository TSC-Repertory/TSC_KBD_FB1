# -*- coding:utf-8 -*-



class ModuleEnum(object):
    """模块枚举"""
    identifier = "skill"


class ModuleEvent(object):
    """模块事件"""
    ModuleRequestSkillRegisterEvent = "ModuleRequestSkillRegisterEvent"  # 请求注册配置事件


class ModuleSkill(object):
    """模块技能"""
    SkillData = {}
