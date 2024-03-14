# -*- coding:utf-8 -*-


from ..system.parser.base import InheritBuildParser


class SkillParser(InheritBuildParser):
    """技能解析器"""
    __mVersion__ = 2
    __identifier__ = "skill"

    @classmethod
    def CheckKeyAvailable(cls, key):
        if key.startswith("_"):
            return False
        return True
