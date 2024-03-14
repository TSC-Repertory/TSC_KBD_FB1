# -*- coding:utf-8 -*-


from ..system.parser.base import InheritBuildParser


class QuestParser(InheritBuildParser):
    """任务解析器"""
    __mVersion__ = 1
    __identifier__ = "quest"

    @classmethod
    def CheckKeyAvailable(cls, key):
        if key.startswith("_"):
            return False
        return True
