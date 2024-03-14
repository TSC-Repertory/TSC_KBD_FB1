# -*- coding:utf-8 -*-



class ModuleEnum(object):
    """模块枚举"""
    identifier = "item"
    food_consume = "item.food_consume"
    recipe_craft = "item.recipe_craft"


class ModuleEvent(object):
    """模块事件"""
    BeforeFoodItemGainNewFoodEvent = "BeforeFoodItemGainNewFoodEvent"  # 即将添加新食物事件
    OnFoodItemGainNewFoodEvent = "OnFoodItemGainNewFoodEvent"  # 添加新食物事件

    ModuleRequestItemFoodConsumeRegisterEvent = "ModuleRequestItemFoodConsumeRegisterEvent"  # 请求注册配置事件
    ModuleRequestItemRecipeCraftRegisterEvent = "ModuleRequestItemRecipeCraftRegisterEvent"  # 请求注册配置事件
