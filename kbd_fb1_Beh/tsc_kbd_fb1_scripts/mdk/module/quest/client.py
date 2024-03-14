# -*- coding:utf-8 -*-


from const import *
from parser import QuestParser
from ..system.base import *

if __name__ == '__main__':
    from parts.entity import QuestEntity


class QuestModuleClient(ModuleClientBase):
    """任务模块客户端"""
    __mVersion__ = 2
    __identifier__ = ModuleEnum.identifier

    def __init__(self):
        super(QuestModuleClient, self).__init__()
        self.ModuleSystem.SetModConfigParser(QuestParser)
        self.rpc = None
        self.finished_load = False
        self.storage = {}

        # 同步属性
        self.finished_quest = []
        self.unfinished_quest = []
        self.active_quest = []
        self.track_quest = None
        self.quest_data = {}

    def OnDestroy(self):
        if self.rpc:
            self.rpc.Discard()
            del self.rpc
        super(QuestModuleClient, self).OnDestroy()

    def ConfigEvent(self):
        super(QuestModuleClient, self).ConfigEvent()
        self.serverEvent.update({
            ModuleEvent.ModuleQuestEntityFinishedLoadEvent: self.ModuleQuestEntityFinishedLoadEvent
        })

    # -----------------------------------------------------------------------------------

    @property
    def server(self):
        # type: () -> QuestEntity
        return self.rpc

    def server_recall(self, recall):
        # type: (any) -> QuestEntity
        return self.rpc(recall)

    # -----------------------------------------------------------------------------------

    def OnUpdateProgress(self, quest_id, value):
        """更新任务进度"""
        self.quest_data[quest_id] = value

    # -----------------------------------------------------------------------------------

    def ModuleQuestEntityFinishedLoadEvent(self, args):
        self.rpc = self.ModuleSystem.CreateRpcModule(self, args["uid"])
        self.storage = args["data"]
        self.finished_load = True
