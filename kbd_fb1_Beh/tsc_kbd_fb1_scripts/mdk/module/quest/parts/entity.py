# -*- coding:utf-8 -*-


import copy
import weakref

from ..const import ModuleQuest, ModuleEvent
from ....common.utils.misc import Misc
from ....interface.data.base import StoragePreset
from ....loader import MDKConfig
from ....server.entity.living_entity import LivingEntity
from ....server.system.base import ServerBaseSystem

if __name__ == '__main__':
    from ..client import QuestModuleClient


class QuestEntity(ServerBaseSystem, LivingEntity, StoragePreset):
    """任务实体"""
    __mVersion__ = 6
    _data_config = {
        "storage_key": "QuestDataStorage",  # 数据键
        "syn_data_key": ""  # 同步数据键 - 客户端缓存
    }

    def __init__(self, target_id):
        ServerBaseSystem.__init__(self, MDKConfig.GetModuleServer())
        LivingEntity.__init__(self, target_id)
        StoragePreset.__init__(self)

        self.rpc, self.rpc_key = None, None
        if self.IsPlayer():
            self.rpc_key = Misc.CreateUUID()
            self.rpc = self.ModuleSystem.CreateRpcModule(self, self.rpc_key)

        # 同步属性
        self.finished_quest = []
        self.unfinished_quest = []
        self.active_quest = []
        self.track_quest = None
        self.quest_data = {}

        # 任务奖励回调
        self._finish_recall = {}

    def OnDestroy(self):
        if self.rpc:
            self.rpc.Discard()
            del self.rpc
        self.SaveData()
        del self._finish_recall
        super(QuestEntity, self).OnDestroy()

    def ConfigRegisterData(self):
        self.RegisterData("finished_quest", [])
        self.RegisterData("unfinished_quest", [])
        self.RegisterData("active_quest", [])
        self.RegisterData("track_quest", None)
        self.RegisterData("quest_data", {})

    # -----------------------------------------------------------------------------------

    @property
    def client(self):
        # type: () -> QuestModuleClient
        return self.rpc(self.id)

    # -----------------------------------------------------------------------------------

    def RegisterFinishQuestRecall(self, quest_id, recall):
        # type: (str, any) -> bool
        """
        注册任务完成回调\n
        - 任务已完成将无法注册
        - 任务完成时将自动触发一次后反注册
        - 回调默认传入: questId
        """
        if quest_id in self.finished_quest:
            return False
        if quest_id not in self._finish_recall:
            self._finish_recall[quest_id] = set()
        finish_recall = self._finish_recall[quest_id]  # type: set
        finish_recall.add(recall)
        return True

    def UnRegisterFinishQuestRecall(self, quest_id, recall):
        # type: (str, any) -> None
        """反注册任务完成回调"""
        if quest_id not in self._finish_recall:
            return
        finish_recall = self._finish_recall[quest_id]  # type: set
        finish_recall.discard(recall)
        if not finish_recall:
            self._finish_recall.pop(quest_id, None)

    # -----------------------------------------------------------------------------------

    def GetFinishedQuest(self):
        # type: () -> list
        """获得完成的任务"""
        return copy.copy(self.finished_quest)

    def GetUnfinishedQuest(self):
        # type: () -> list
        """获得尚未完成的任务"""
        return copy.copy(self.unfinished_quest)

    def GetActiveQuest(self):
        # type: () -> list
        """获得当前激活的任务"""
        return copy.copy(self.active_quest)

    def GetQuestData(self):
        # type: () -> dict
        """获得任务数据"""
        return copy.copy(self.quest_data)

    def GetTrackQuest(self):
        # type: () -> str
        """获得当前追踪的任务"""
        return self.track_quest

    def RegisterQuest(self, quest_id):
        # type: (str) -> bool
        """注册任务"""
        if self.IsQuestFinished(quest_id) or self.IsQuestActive(quest_id):
            return False
        self.quest_data[quest_id] = 0
        self.active_quest.append(quest_id)
        self.RequestSaveData()
        # print "[suc]", "register quest: %s" % quest_id
        return True

    def ResetQuest(self, quest_id):
        # type: (str) -> bool
        """重置任务"""
        save_data = False
        if quest_id in self.finished_quest:
            finished_quest = set(self.finished_quest)
            finished_quest.discard(quest_id)
            self.finished_quest = list(finished_quest)
            save_data = True
        elif quest_id in self.active_quest:
            active_quest = set(self.active_quest)
            active_quest.discard(quest_id)
            self.active_quest = list(active_quest)
            save_data = True
        # todo: 处理track_quest逻辑

        if save_data:
            self.RegisterQuest(quest_id)
            return True
        return False

    def GetProgress(self, quest_id):
        # type: (str) -> int
        """获取进度"""
        if not self.IsQuestActive(quest_id) or self.IsQuestFinished(quest_id):
            return -1
        return self.quest_data[quest_id]

    def AddProgress(self, quest_id, value):
        # type: (str, int) -> bool
        """添加进度"""
        data = self.GetProgress(quest_id)
        if data < 0 or value <= 0:
            return False
        value += data
        self.OnUpdateProgress(quest_id, data, value)
        # print "[suc]", "add progress: <%s> %s" % (quest_id, value)
        self.RequestSaveData()
        return True

    def SetProgress(self, quest_id, value):
        # type: (str, int) -> bool
        """设置进度"""
        data = self.GetProgress(quest_id)
        if data < 0 or value < 0 or data == value:
            return False
        self.OnUpdateProgress(quest_id, data, value)
        # print "[suc]", "set progress: <%s> %s" % (quest_id, data)
        self.RequestSaveData()
        return True

    # -----------------------------------------------------------------------------------

    def IsQuestFinished(self, quest_id):
        # type: (str) -> bool
        """任务是否已经完成"""
        return quest_id in self.finished_quest

    def IsQuestActive(self, quest_id):
        # type: (str) -> bool
        """任务是否激活"""
        return quest_id in self.active_quest

    def _CheckProgress(self, quest_id, data):
        # type: (str, dict) -> bool
        """检测进度是否达成"""
        config = ModuleQuest.QuestData[quest_id]  # type: dict
        goals = config["goals"]
        # 数据修正
        if data["after"] < 0:
            data["after"] = 0
        # 判断达到最大值
        if data["after"] < goals:
            return False
        # 设置成目标值
        data["after"] = goals

        # 完成任务 - 不删除数据
        # self.quest_data.pop(quest_id, None)
        self.finished_quest.append(quest_id)
        self.finished_quest = list(set(self.finished_quest))

        # 奖励解析

        # 奖励修正
        pack = {
            "cancel": False,
            "targetId": self.id,
            "questId": quest_id,
            "rewards": []
        }
        self.BroadcastEvent(ModuleEvent.ModuleBeforeQuestRewardEvent, pack)
        if not pack.get("cancel"):
            self.OnActiveQuestReward(config)
            # 调用注册回调 [有必要每个任务都回调吗？]
            if quest_id in self._finish_recall:
                finish_recall = self._finish_recall[quest_id]  # type: set
                for recall in list(finish_recall):
                    if callable(recall):
                        recall(quest_id)
                finish_recall.clear()
                self._finish_recall.pop(quest_id, None)

        self.BroadcastEvent(ModuleEvent.ModuleOnFinishedQuestEvent, {
            "targetId": self.id,
            "questId": quest_id
        })
        return True

    # -----------------------------------------------------------------------------------

    def GetData(self, key):
        return self.GetStorage(key)

    def SetData(self, key, value):
        self.SetStorage(key, value)

    def SaveQuestData(self):
        """保存任务数据"""
        # print "[suc]", "SaveQuestData"
        self.PackData()
        self.SaveData()

    def RequestSaveData(self):
        """请求保存数据"""
        self.QuestModule.AddTargetSaveData(self.id)

    # -----------------------------------------------------------------------------------

    def OnFinishedLoadData(self):
        storage = self.QuestModule.quest_recall.pop(self.id, None)  # type: set
        if storage:
            for recall in storage:
                recall(weakref.proxy(self))
        if self.IsPlayer():
            self.NotifyToClient(self.id, ModuleEvent.ModuleQuestEntityFinishedLoadEvent, {
                "uid": self.rpc_key,
                "data": self.storage
            })

    def OnActiveQuestReward(self, config):
        # type: (dict) -> None
        """执行任务奖励"""
        # print "[suc]", "OnActiveQuestReward"

    def OnUpdateProgress(self, quest_id, before, after):
        # type: (str, int, int) -> bool
        """进度更新触发"""
        pack = {"cancel": False, "questId": quest_id, "before": before, "after": after}
        # 是否取消修改的事件
        self.BroadcastEvent(ModuleEvent.ModuleUpdateQuestProgressEvent, pack)
        if pack.pop("cancel"):
            return False

        # 判断是否完成任务
        self._CheckProgress(quest_id, pack)
        # 设置修正数据[被其他脚本修正|最值修正]
        value = pack["after"]
        if before == value:
            return False
        self.quest_data[quest_id] = value
        # 客户端同步数据
        if self.rpc:
            self.client.OnUpdateProgress(quest_id, value)
        return True
