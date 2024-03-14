# -*- coding:utf-8 -*-


from mod.common.minecraftEnum import ItemPosType

from ..block.predicate import LocationPredicate
from ..item.predicate import ItemPredicate
from ..parts.base import PredicateBase


# 实体断言
class EntityPredicate(PredicateBase):
    """实体断言"""
    __mVersion__ = 3

    def __init__(self, entity_id, data, context=None):
        super(EntityPredicate, self).__init__(data, context)
        self.id = entity_id
        self.engine_type_str = self.comp_factory.CreateEngineType(self.id).GetEngineTypeStr()

    def Parse(self):
        predicates = self.data["predicate"]  # type: dict
        for predicate in predicates.items():
            if not self.ParsePredicate(predicate):
                return False
        return True

    # 解析子断言
    def ParsePredicate(self, data):
        # type: (tuple) -> bool
        """
        解析子断言\n
        - type: str
        - gamemode: int
        - location: LocationPredicate
        - stepping_on: LocationPredicate
        - equipment: dict - ItemPredicate
        - vehicle: EntityPredicate
        - targeted_entity: EntityPredicate
        """
        key, value = data
        # 实体类型检测
        if key == "type":
            if not self.engine_type_str == value:
                return False
        # 玩家游戏模式检测
        elif key == "gamemode":
            if not self.engine_type_str == "minecraft:player":
                return False
            if self.comp_factory.CreateGame(self.id).GetGameType() != value:
                return False
        # 实体效果检测
        elif key == "effects":
            if not self.CheckTargetEffect(value):
                return False
        # 装备检测
        elif key == "equipment":
            if not self.CheckEquipment(value):
                return False
        # 位置检测
        elif key == "location":
            check_pos = self.comp_factory.CreatePos(self.id).GetFootPos()
            if not LocationPredicate(check_pos, value, self.context).GetResult():
                return False
        # 踩着方块检测
        elif key == "stepping_on":
            check_pos = self.comp_factory.CreatePos(self.id).GetFootPos()
            check_pos = tuple(map(lambda x, y: x - y, check_pos, (0, -1, 0)))
            if not LocationPredicate(check_pos, value, self.context).GetResult():
                return False
        # 检测坐骑生物
        elif key == "vehicle":
            # 玩家专属接口
            if self.engine_type_str != "minecraft:player":
                return False
            ride_id = self.comp_factory.CreateRide(self.id).GetEntityRider()
            if ride_id == "-1" or not EntityPredicate(ride_id, value, self.context).GetResult():
                return False
        # 检测仇恨目标生物
        elif key == "targeted_entity":
            target_id = self.comp_factory.CreateAction(self.id).GetAttackTarget()
            if target_id == "-1" or not EntityPredicate(target_id, value, self.context).GetResult():
                return False
        return True

    # 检测目标装备
    def CheckEquipment(self, data):
        # type: (dict) -> bool
        """检测目标装备"""
        item_comp = self.comp_factory.CreateItem(self.predicate_id)
        # 装备物品检测
        slots = ["head", "chest", "legs", "feet"]
        for index, slot in enumerate(slots):
            if slot not in data:
                continue
            storage = data[slot]  # type: dict
            item_dict = item_comp.GetPlayerItem(ItemPosType.ARMOR, index, True)
            if not item_dict:
                return False
            if not ItemPredicate(item_dict, storage, self.context).GetResult():
                return False
        # 主手物品检测
        key = "mainhand"
        if key in data:
            storage = data[key]
            item_dict = item_comp.GetEntityItem(ItemPosType.CARRIED, getUserData=True)
            if not item_dict:
                return False
            if not ItemPredicate(item_dict, storage, self.context).GetResult():
                return False
        # 副手物品检测
        key = "mainhand"
        if key in data:
            storage = data[key]
            item_dict = item_comp.GetEntityItem(ItemPosType.OFFHAND, getUserData=True)
            if not item_dict:
                return False
            if not ItemPredicate(item_dict, storage, self.context).GetResult():
                return False
        return True

    # 检测目标效果
    def CheckTargetEffect(self, data):
        # type: (dict) -> bool
        """检测目标效果"""
        effect_comp = self.comp_factory.CreateEffect(self.id)
        effects = effect_comp.GetAllEffects()
        if not effects and data:
            return False
        # 当前的效果数据
        effect_map = {effect.pop("effectName"): effect for effect in effects}
        check_keys = ["amplifier", "duration"]
        for effect_id, storage in data.iteritems():
            assert isinstance(effect_id, dict)
            if effect_id not in effects:
                return False
            if not storage:
                continue
            effect_data = effect_map[effect_id]  # type: dict
            for key in check_keys:
                if key in storage and storage[key] != effect_data[key]:
                    return False
        return True


# 伤害断言
class DamagePredicate(PredicateBase):
    """伤害断言"""
    __mVersion__ = 1

    def __init__(self, data, context):
        super(DamagePredicate, self).__init__(data, context)
        self.damage_pack = self.context.get("event_pack", {})

    def Parse(self):
        # 伤害类型检测
        if "cause" in self.data:
            cause = self.data["cause"]
            if not cause == self.damage_pack.get("cause"):
                return False
        # 直接造成伤害的实体检测
        if "direct_entity" in self.data:
            projectile_id = self.damage_pack.get("projectileId")
            data = self.data["direct_entity"]
            if not projectile_id:
                return False
            if not EntityPredicate(projectile_id, data, self.context).GetResult():
                return False
        # 伤害源实体检测
        if "source_entity" in self.data:
            source_id = self.damage_pack.get("srcId")
            data = self.data["source_entity"]
            if not source_id:
                return False
            return EntityPredicate(source_id, data, self.context).GetResult()
        return True
