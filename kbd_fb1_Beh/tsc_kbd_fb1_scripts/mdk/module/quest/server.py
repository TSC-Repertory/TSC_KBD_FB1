# -*- coding:utf-8 -*-


import weakref

from const import *
from parser import QuestParser
from parts.entity import QuestEntity
from ..system.preset import *


class QuestModuleServer(LoadConfigModuleServer):
    """任务模块服务端"""
    __mVersion__ = 4
    __identifier__ = ModuleEnum.identifier
    _ModuleRequestRegisterEvent = ModuleEvent.ModuleRequestQuestRegisterEvent
    _RegisterDataParser = QuestParser.GetId()

    def __init__(self):
        super(QuestModuleServer, self).__init__()
        self.dirty_player = set()
        self.quest_storage = {}
        self.save_data_target = set()
        self.quest_recall = {}

    def OnDestroy(self):
        self.ModuleSystem.UnRegisterUpdateSecond(self.OnUpdateSecond)
        for player in self.quest_storage.values():
            player.OnDestroy()
        super(QuestModuleServer, self).OnDestroy()

    def ConfigEvent(self):
        super(QuestModuleServer, self).ConfigEvent()
        self.defaultEvent.update({
            ServerEvent.PlayerIntendLeaveServerEvent: self.PlayerIntendLeaveServerEvent,
        })

    # -----------------------------------------------------------------------------------

    def GetDefaultConfig(self):
        return ["quests/root.json"]

    # -----------------------------------------------------------------------------------

    def OnUpdateSecond(self):
        """秒更新"""
        if self.save_data_target:
            for target_id in list(self.save_data_target):
                target = self.quest_storage.get(target_id)  # type: QuestEntity
                if target:
                    target.SaveQuestData()
            self.save_data_target.clear()

    def OnLoadModConfig(self, data):
        ModuleQuest.QuestData = data
        for player_id in self.dirty_player:
            player_quest = QuestEntity(player_id)
            self.quest_storage[player_id] = player_quest
            player_quest.LoadData()
        self.dirty_player.clear()
        self.ModuleSystem.RegisterUpdateSecond(self.OnUpdateSecond)
        # 注册世界任务
        level_id = serverApi.GetLevelId()
        level_quest = QuestEntity(level_id)
        self.quest_storage[level_id] = level_quest
        # 导入世界数据
        level_quest.LoadData()
        return True

    # -----------------------------------------------------------------------------------

    def AddTargetSaveData(self, target_id):
        """添加玩家数据保存"""
        self.save_data_target.add(target_id)

    def AddTargetProgress(self, target_id, quest_id, quest_value=1):
        # type: (str, str, any) -> bool
        """添加目标任务进度"""
        target = self.quest_storage.get(target_id)  # type: QuestEntity
        if target:
            return target.AddProgress(quest_id, quest_value)
        return False

    def SetTargetProgress(self, target_id, quest_id, quest_value):
        # type: (str, str, any) -> bool
        """设置目标任务进度"""
        target = self.quest_storage.get(target_id)  # type: QuestEntity
        if target:
            return target.AddProgress(quest_id, quest_value)
        return False

    def IsTargetFinishedQuest(self, target_id, quest_id):
        # type: (str, str) -> bool
        """目标是否完成任务"""
        target = self.quest_storage.get(target_id)  # type: QuestEntity
        if target:
            return target.IsQuestFinished(quest_id)
        return False

    def RegisterTargetQuest(self, target_id, quest_id):
        # type: (str, str) -> bool
        """注册目标任务"""
        target = self.quest_storage.get(target_id)  # type: QuestEntity
        if target:
            return target.RegisterQuest(quest_id)
        print "[warn]", "Invalid target id: %s" % target_id
        return False

    def GetQuestEntity(self, target_id, recall):
        """获得任务实体"""
        target = self.quest_storage.get(target_id)  # type: QuestEntity
        if target:
            recall(weakref.proxy(target))
            return
        if target_id not in self.quest_recall:
            self.quest_recall[target_id] = set()
        storage = self.quest_recall[target_id]  # type: set
        storage.add(recall)

    @classmethod
    def GetQuestEntityCls(cls):
        """获得任务实体类"""
        return QuestEntity

    # -----------------------------------------------------------------------------------

    def ClientLoadAddonsFinishServerEvent(self, args):
        player_id = args["playerId"]
        if self._load_data:
            player_quest = QuestEntity(player_id)
            self.quest_storage[player_id] = player_quest
            player_quest.LoadData()
            return
        self.dirty_player.add(player_id)

    def PlayerIntendLeaveServerEvent(self, args):
        player_id = args["playerId"]
        player = self.quest_storage.pop(player_id, None)  # type: QuestEntity
        if player:
            player.OnDestroy()
