# -*- coding:utf-8 -*-



class ModuleEnum(object):
    """模块枚举"""
    identifier = "world"


class TimeState(object):
    """时间状态"""
    sunrise = "sunrise"  # 23000
    day = "day"  # 1000
    noon = "noon"  # 6000
    afternoon = "afternoon"  # 6100
    sunset = "sunset"  # 12000
    night = "night"  # 13000
    midnight = "midnight"  # 18000

    DayState = [sunrise, day, noon, afternoon, sunset]
    NightState = [night, midnight]

    @classmethod
    def GetPreState(cls, time_tick):
        # type: (int) -> str
        """获得当前状态"""
        time_tick = time_tick % 24000
        if time_tick < 1000 or time_tick >= 23000:
            return cls.sunrise
        elif time_tick < 6000:
            return cls.day
        elif time_tick < 6100:
            return cls.noon
        elif time_tick < 12000:
            return cls.afternoon
        elif time_tick < 18000:
            return cls.night
        else:
            return cls.midnight


class ModuleEvent(object):
    """模块事件"""
    # 只读事件
    OnWorldSunriseEvent = "OnWorldSunriseEvent"
    OnWorldDayEvent = "OnWorldDayEvent"
    OnWorldNoonEvent = "OnWorldNoonEvent"
    OnWorldAfterNoonEvent = "OnWorldAfterNoonEvent"
    OnWorldSunsetEvent = "OnWorldSunsetEvent"
    OnWorldNightEvent = "OnWorldNightEvent"
    OnWorldMidnightEvent = "OnWorldMidnightEvent"

    OnWorldUpdateDayEvent = "OnWorldUpdateDayEvent"

    RequestWorldDayEvent = "RequestWorldDayEvent"
