# -*- coding:utf-8 -*-


from const import *
from ..system.base import *

from parts.buff import Buff


class BuffModuleServer(ModuleServerBase):
    """效果模块服务端"""
    __mVersion__ = 1
    __identifier__ = ModuleEnum.identifier

    def __init__(self):
        super(BuffModuleServer, self).__init__()
        # 增益类缓存
        self.buff_cls = {}
        # 增益实例缓存
        self.buff_entity = {}

        self.update_timer = None

    def OnDestroy(self):
        if self.update_timer:
            self.game_comp.CancelTimer(self.update_timer)
        del self.update_timer
        super(BuffModuleServer, self).OnDestroy()

    def ConfigEvent(self):
        super(BuffModuleServer, self).ConfigEvent()
        self.serverEvent.update({
            ServerEvent.ServerModuleFinishedLoadEvent: self.ServerModuleFinishedLoadEvent,
        })

    def RegisterBuffClass(self, buff_cls):
        # type: (Buff) -> bool
        """注册增益类"""
        buff_type_id = buff_cls.GetBuffTypeId()
        if buff_type_id in self.buff_cls:
            return False
        self.buff_cls[buff_type_id] = buff_cls

    # -----------------------------------------------------------------------------------

    def OnUpdateSecond(self):
        """秒更新"""

    # -----------------------------------------------------------------------------------

    def ServerModuleFinishedLoadEvent(self, _):
        def active():
            self.flag_finished_load = True
            self.update_timer = self.game_comp.AddRepeatedTimer(1, self.OnUpdateSecond)

        self.DelayTickFunc(30, active)
