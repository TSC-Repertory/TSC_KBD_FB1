# -*- coding:utf-8 -*-


import math

from mod.common.minecraftEnum import AttrType

from entity import RawEntity, Entity
from ...common.utils.misc import Misc


class AttrEntity(Entity):
    """属性实体基类"""
    __mVersion__ = 3

    def __init__(self, entityId):
        super(AttrEntity, self).__init__(entityId)
        self.data_comp = self.comp_factory.CreateExtraData(self.id)

    def InitHealth(self, value):
        # type: (int) -> None
        """
        初始化血量\n
        - 会同时设置最大值和当前值
        - 一般用生物血量初始化
        """
        self.SetMaxHealth(value)
        self.SetHealth(value)

    def GetHealth(self):
        # type: () -> float
        """获取实体生命"""
        return self.attr_comp.GetAttrValue(AttrType.HEALTH)

    def SetHealth(self, value):
        # type: (int) -> None
        """设置实体生命"""
        self.attr_comp.SetAttrValue(AttrType.HEALTH, value)

    def AddHealth(self, value):
        # type: (int) -> None
        """增加实体目前生命"""
        value = min(int(self.GetHealth() + value), int(self.GetMaxHealth()))
        self.SetHealth(value)

    def AddRateHealth(self, rate):
        # type: (float) -> None
        """按百分比增加实体生命"""
        self.AddHealth(int(math.ceil(self.GetMaxHealth() * rate)))

    def RemoveHealth(self, value):
        # type: (int) -> None
        """减少生命，不通过原版Hurt方式"""
        self.SetHealth(int(self.GetHealth() - value))

    def RemoveRateHealth(self, rate):
        # type: (float) -> None
        """百分比减少生命，不通过原版Hurt方式"""
        self.RemoveHealth(int(math.ceil(self.GetMaxHealth() * rate)))

    def GetRateHealth(self):
        # type: () -> float
        """获得生命百分比"""
        return float(self.GetHealth()) / self.GetMaxHealth()

    def SetRateHealth(self, rate):
        # type: (float) -> None
        """设置百分比生命"""
        rate = Misc.GetClamp(rate, 0, 1)
        value = self.GetRateHealthValue(rate, 0)
        self.SetHealth(value)

    def GetRateHealthValue(self, rate, least=1):
        # type: (float, int) -> int
        """获得最大值的百分比的值"""
        max_health = self.GetMaxHealth()
        if not max_health:
            max_health = 1
        return max(least, int(rate * max_health))

    def GetMaxHealth(self):
        # type: (any) -> float
        """获取实体最大生命"""
        return self.attr_comp.GetAttrMaxValue(AttrType.HEALTH)

    def SetMaxHealth(self, value):
        # type: (int) -> None
        """设置实体最大生命"""
        self.attr_comp.SetAttrMaxValue(AttrType.HEALTH, value)

    # -----------------------------------------------------------------------------------

    def GetAttack(self):
        # type: () -> int
        """获取攻击属性值"""
        return int(self.attr_comp.GetAttrValue(AttrType.DAMAGE))

    def SetAttack(self, value):
        # type: (int) -> None
        """设置实体攻击属性"""
        self.attr_comp.SetAttrMaxValue(AttrType.DAMAGE, value)
        self.attr_comp.SetAttrValue(AttrType.DAMAGE, value)

    def SetRateAttack(self, rate):
        # type: (float) -> None
        """根据目前攻击百分比调整"""
        value = int(self.GetAttack() * rate)
        self.SetAttack(value)

    # -----------------------------------------------------------------------------------

    def GetMovementSpeed(self):
        # type: () -> float
        """获取移速属性值"""
        return self.attr_comp.GetAttrValue(AttrType.SPEED)

    def SetMovementSpeed(self, value):
        # type: (float) -> None
        """设置实体移速属性"""
        self.attr_comp.SetAttrValue(AttrType.SPEED, value)

    def SetRateSpeed(self, rate):
        # type: (float) -> None
        """根据目前速度百分比调整"""
        value = self.GetMovementSpeed() * rate
        self.SetMovementSpeed(value)

    # -----------------------------------------------------------------------------------

    def SetJumpPower(self, power):
        # type: (float) -> None
        """设置弹跳力度"""
        self.comp_factory.CreateGravity(self.id).SetJumpPower(power)

    def SetJumpPowerRate(self, rate):
        # type: (float) -> None
        """设置百分比弹跳力度 - 基于原本"""
        self.SetJumpPower(0.42 * rate)

    def ResetJumpPower(self):
        """重置弹跳力度"""
        self.comp_factory.CreateGravity(self.id).SetJumpPower(0.42)

    # -----------------------------------------------------------------------------------

    def HasEffect(self, effectName):
        # type: (str) -> bool
        """判定实体是否存在指定药水效果"""
        effects = self.comp_factory.CreateEffect(self.id).GetAllEffects()
        if not effects:
            return False
        effects = set(effect["effectName"] for effect in effects)
        return effectName in effects

    def AddEffect(self, effectName, duration=10, amplifier=0, showParticles=True):
        # type: (str, int, int, bool) -> bool
        """设置实体药水效果"""
        return RawEntity.AddEffect(self.id, effectName, duration, amplifier, showParticles)

    def DelEffect(self, effectName):
        # type: (str) -> bool
        """移除实体药水效果"""
        return self.comp_factory.CreateEffect(self.id).RemoveEffectFromEntity(effectName)

    def GetEffect(self, effectName):
        # type: (str) -> dict
        """
        获取目标药水效果字典\n
        无此效果返回{}\n
        - effectName: str 药水名称
        - duration: int 持续时间
        - amplifier: int 药水等级
        """
        for effect in self.GetAllEffect():
            assert isinstance(effect, dict)
            if effect.get("effectName") == effectName:
                return effect
        return {}

    def GetAllEffect(self):
        # type: () -> list
        """获取所有实体药水效果"""
        effectList = self.comp_factory.CreateEffect(self.id).GetAllEffects()
        return effectList if effectList else []

    def ClearEffect(self):
        # type: () -> None
        """清除实体所有药水效果"""
        effectComp = self.comp_factory.CreateEffect(self.id)
        effectList = effectComp.GetAllEffects()
        if not effectList:
            return
        for effect in effectList:
            effectComp.RemoveEffectFromEntity(effect["effectName"])

    # -----------------------------------------------------------------------------------

    def HasStorage(self, storageKey):
        # type: (str) -> bool
        """判断实体是否有自定义数据"""
        return self.data_comp.GetExtraData(storageKey) is not None

    def DelStorage(self, storageKey):
        # type: (str) -> bool
        """删除实体自定义数据"""
        return self.data_comp.CleanExtraData(storageKey)

    def GetStorage(self, storageKey):
        # type: (str) -> dict
        """获取实体自定义数据"""
        if self.data_comp.GetExtraData(storageKey) is None:
            self.data_comp.SetExtraData(storageKey, {})
        storage = self.data_comp.GetExtraData(storageKey)

        return storage

    def GetAllStorage(self):
        # type: () -> dict
        """获取所有实体自定义数据"""
        return self.data_comp.GetWholeExtraData()

    def SetStorage(self, key, storage):
        # type: (str, dict) -> bool
        """设置实体自定义数据"""
        return self.data_comp.SetExtraData(key, storage)

    def GetDataByKey(self, dataKey, storageKey):
        # type: (str, str) -> any
        """根据键值获取某个自定义数据"""
        storage = self.GetStorage(storageKey)
        return storage.get(dataKey)

    def ConfigFirstLoadRecall(self, key, recall):
        """
        配置首次登录事件\n
        只在加载模组时执行一次的内容
        """
        storage = self.GetStorage(key)
        if not storage:
            self.SetStorage(key, {"execute": True})
            if callable(recall):
                recall(self.id)
