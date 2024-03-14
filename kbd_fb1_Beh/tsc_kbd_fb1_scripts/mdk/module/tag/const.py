# -*- coding:utf-8 -*-



class ModuleEnum(object):
    """模块枚举"""
    identifier = "tag"


class ModuleEvent(object):
    """模块事件"""
    ModuleRequestTagRegisterEvent = "ModuleRequestTagRegisterEvent"  # 请求注册配置事件
    ModuleRequestSynTagDataEvent = "ModuleRequestSynTagDataEvent"  # 同步标签数据事件


class ModuleTag(object):
    """模块标签"""
    TagStorage = {}

    @classmethod
    def GetTag(cls, path):
        # type: (str) -> list
        """获得标签列表"""
        return cls.TagStorage.get(path, [])
