# -*- coding:utf-8 -*-


from const import *
from ..system.base import *
from ...interface.data.base import StorageBase


class WorldModuleServer(ModuleServerBase, StorageBase):
    """
    世界模块服务端\n
    - 启用模块后在每次切换时间状态时会强制修正游戏时间
    """
    __mVersion__ = 6
    __identifier__ = ModuleEnum.identifier

    _state_event_map = {
        TimeState.sunrise: ModuleEvent.OnWorldSunriseEvent,
        TimeState.day: ModuleEvent.OnWorldDayEvent,
        TimeState.noon: ModuleEvent.OnWorldNoonEvent,
        TimeState.afternoon: ModuleEvent.OnWorldAfterNoonEvent,
        TimeState.sunset: ModuleEvent.OnWorldSunsetEvent,
        TimeState.night: ModuleEvent.OnWorldNightEvent,
        TimeState.midnight: ModuleEvent.OnWorldMidnightEvent,
    }

    def __init__(self):
        super(WorldModuleServer, self).__init__()
        self.data_key = MDKConfig.ModuleNamespace + "WorldStorage"
        self.dim_comp = self.comp_factory.CreateDimension(serverApi.GetLevelId())
        self.time_comp = self.comp_factory.CreateTime(serverApi.GetLevelId())

        self.tick15 = 0
        self.syn_data = False

        self.pre_day = 1
        self.last_time_tick = self.dim_comp.GetLocalTime(GameDimension.Overworld)
        self.last_time = self.last_time_tick % 24000

        self.time_state = TimeState.GetPreState(self.last_time)

        self.storage = self.LoadData()

    def ConfigEvent(self):
        super(WorldModuleServer, self).ConfigEvent()
        self.defaultEvent.update({
            ServerEvent.OnScriptTickServer: self.OnScriptTickServer
        })
        self.serverEvent.update({
            ModuleEvent.RequestWorldDayEvent: self.RequestWorldDayEvent
        })

        # -----------------------------------------------------------------------------------

    def SaveData(self):
        self.storage = {
            "pre_day": self.pre_day,
            "last_time": self.last_time,
            "last_time_tick": self.last_time_tick,
        }
        self.SetLevelStorage(self.data_key, self.storage)

    def LoadData(self):
        storage = self.GetLevelStorage(self.data_key)
        if storage:
            self.pre_day = storage.get("pre_day")
            self.last_time = storage.get("last_time")
            self.last_time_tick = storage.get("last_time_tick")
        return storage

    # -----------------------------------------------------------------------------------

    def OnUpdateTick15(self):
        pre_time_tick = self.dim_comp.GetLocalTime(GameDimension.Overworld)
        # -----------------------------------------------------------------------------------
        self.last_time_tick = pre_time_tick
        self.last_time = self.last_time_tick % 24000
        # -----------------------------------------------------------------------------------
        new_state = TimeState.GetPreState(self.last_time_tick)
        if new_state == self.time_state:
            return
        # 时间矫正
        self.time_comp.SetTime(self.last_time + 24000 * self.pre_day)
        self.syn_data = True
        if self.time_state in TimeState.NightState and new_state in TimeState.DayState:
            self.pre_day += 1
            self.BroadcastEvent(ModuleEvent.OnWorldUpdateDayEvent, {"day": self.pre_day})
            self.BroadcastToAllClient(ModuleEvent.OnWorldUpdateDayEvent, {"day": self.pre_day})
        self.time_state = new_state
        # -----------------------------------------------------------------------------------
        event = self._state_event_map[self.time_state]
        full_mood = self.pre_day % 8 == 0
        self.BroadcastEvent(event, {"day": self.pre_day, "full_moon": full_mood})
        self.BroadcastToAllClient(event, {"day": self.pre_day, "full_moon": full_mood})

    # -----------------------------------------------------------------------------------

    def OnScriptTickServer(self):
        self.tick15 += 1
        if self.tick15 % 5 == 0:
            if self.syn_data:
                self.syn_data = False
                self.SaveData()
        if self.tick15 >= 15:
            self.tick15 = 0
            self.OnUpdateTick15()

    def RequestWorldDayEvent(self, args):
        """请求世界日期事件"""
        args["day"] = self.pre_day
