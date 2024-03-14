# -*- coding:utf-8 -*-


from const import *
from parser import SkillParser
from parts.entity import SkillConfigEntity
from ...module.system.preset import *


class SkillModuleServer(LoadConfigModuleServer):
    """技能模块服务端"""
    __mVersion__ = 2
    __identifier__ = ModuleEnum.identifier
    _ModuleRequestRegisterEvent = ModuleEvent.ModuleRequestSkillRegisterEvent
    _RegisterDataParser = SkillParser.GetId()

    def GetDefaultConfig(self):
        return ["skills/root.json"]

    # -----------------------------------------------------------------------------------

    @classmethod
    def CastSkill(cls, entityId, skillId, context):
        # type: (str, str, dict) -> any
        """
        释放技能配置\n
        保留字\n
        - caster: str 释放者Id
        - projectile_hit_pos: tuple 抛射物击中位置
        - detector_pos: tuple 上一个检测体生成位置
        - detector_drt: tuple 上一个检测体生成时目标朝向
        """
        if skillId not in ModuleSkill.SkillData:
            print "[warn]", "Invalid skill id: %s" % skillId
            return
        config = ModuleSkill.SkillData[skillId]  # type: dict
        # -----------------------------------------------------------------------------------
        if "type" not in config:
            print "[warn]", "Invalid skill id: %s" % skillId
            return
        context["caster"] = entityId
        skill_entity = SkillConfigEntity(entityId)
        skill_entity.ParseSkillConfig(config)(context)
        return skill_entity

    # -----------------------------------------------------------------------------------

    def OnLoadModConfig(self, data):
        ModuleSkill.SkillData = data
        return True
