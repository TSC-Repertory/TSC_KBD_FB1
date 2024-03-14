# -*- coding:utf-8 -*-



class ModuleEnum(object):
    """模块枚举"""
    identifier = "quest"


class ModuleEvent(object):
    """模块事件"""
    ModuleRequestQuestRegisterEvent = "ModuleRequestQuestRegisterEvent"
    ModuleOnFinishedQuestEvent = "ModuleOnFinishedQuestEvent"
    ModuleBeforeQuestRewardEvent = "ModuleBeforeQuestRewardEvent"
    ModuleUpdateQuestProgressEvent = "ModuleUpdateQuestProgressEvent"
    # 任务实体完成加载事件 - 此时可注册任务
    ModuleQuestEntityFinishedLoadEvent = "ModuleQuestEntityFinishedLoadEvent"


class ModuleQuest(object):
    """模块任务"""
    QuestData = {}
    # 登录后自动注册任务
    LoadRegisterQuest = set()
