# -*- coding:utf-8 -*-


import mod.server.extraServerApi as serverApi
from ..parts.base import ConditionBase


# 天气检测条件
class WeatherCheckCondition(ConditionBase):
    """天气检测条件"""
    __mVersion__ = 1

    def __init__(self, data, context=None):
        super(WeatherCheckCondition, self).__init__(data, context)
        self.weather_comp = self.comp_factory.CreateWeather(serverApi.GetLevelId())

    def Parse(self):
        is_pass = False
        if "raining" in self.data:
            is_pass &= self.data["raining"] & self.IsRaining()
        if "thundering" in self.data:
            is_pass &= self.data["thundering"] & self.IsThundering()
        return is_pass

    def IsRaining(self):
        # type: () -> bool
        """是否在下雨"""
        return self.weather_comp.IsRaining()

    def IsThundering(self):
        # type: () -> bool
        """是否在打雷"""
        return self.weather_comp.IsThunder()
