# -*- coding:utf-8 -*-



class ModuleEnum(object):
    """模块枚举"""
    identifier = "predicate"


class ModuleEvent(object):
    """模块事件"""
    ModuleRequestPredicateRegisterEvent = "ModuleRequestPredicateRegisterEvent"  # 请求注册配置事件


class ModulePredicate(object):
    """模块断言"""
    PredicateData = {}


# 条件枚举
class ConditionEnum(object):
    """条件枚举"""
    default = "default"
    alternative = "alternative"
    inverted = "inverted"
    reference = "reference"

    entity_properties = "entity_properties"
    block_state_property = "block_state_property"
    damage_source_properties = "damage_source_properties"

    location_check = "location_check"
    time_check = "time_check"
    weather_check = "weather_check"
    value_check = "value_check"

    match_tool = "match_tool"
    random_chance = "random_chance"

    Available_Key = (
        default, alternative, inverted, reference,
        entity_properties, block_state_property, damage_source_properties,
        location_check, time_check, weather_check, value_check,
        random_chance, match_tool,
    )


# -----------------------------------------------------------------------------------


class ActionTrigger(object):
    """行为触发"""
    AddHealth = "add_health"
    AddHealthReach = "add_health_reach"
    DealDamage = "deal_damage"
    TakeDamage = "take_damage"
    Crit = "crit"
    InventoryChanged = "inventory_changed"
    Impossible = "impossible"
    ChangedDimension = "changed_dimension"
    PlayerKilledEntity = "player_killed_entity"
    # -----------------------------------------------------------------------------------
    # tame_animal = "tame_animal"
    # consume_item = "consume_item"
    # listen_server_event = "listen_server_event"
    # -----------------------------------------------------------------------------------
    # allay_drop_item_on_block = "allay_drop_item_on_block"
    # avoid_vibration = "avoid_vibration"
    # bee_nest_destroyed = "bee_nest_destroyed"
    # bred_animals = "bred_animals"
    # brewed_potion = "brewed_potion"
    # channeled_lightning = "channeled_lightning"
    # construct_beacon = "construct_beacon"
    # cured_zombie_villager = "cured_zombie_villager"
    # effects_changed = "effects_changed"
    # enchanted_item = "enchanted_item"
    # enter_block = "enter_block"
    # entity_hurt_player = "entity_hurt_player"
    # entity_killed_player = "entity_killed_player"
    # fall_from_height = "fall_from_height"
    # filled_bucket = "filled_bucket"
    # fishing_rod_hooked = "fishing_rod_hooked"
    # hero_of_the_village = "hero_of_the_village"
    # item_durability_changed = "item_durability_changed"
    # item_used_on_block = "item_used_on_block"
    # kill_mob_near_sculk_catalyst = "kill_mob_near_sculk_catalyst"
    # killed_by_crossbow = "killed_by_crossbow"
    # levitation = "levitation"
    # lightning_strike = "lightning_strike"
    # location = "location"
    # nether_travel = "nether_travel"
    # placed_block = "placed_block"
    # player_generates_container_loot = "player_generates_container_loot"
    # player_hurt_entity = "player_hurt_entity"
    # player_interacted_with_entity = "player_interacted_with_entity"
    # recipe_unlocked = "recipe_unlocked"
    # shot_crossbow = "shot_crossbow"
    # slept_in_bed = "slept_in_bed"
    # slide_down_block = "slide_down_block"
    # started_riding = "started_riding"
    # summoned_entity = "summoned_entity"
    # target_hit = "target_hit"
    # thrown_item_picked_up_by_entity = "thrown_item_picked_up_by_entity"
    # thrown_item_picked_up_by_player = "thrown_item_picked_up_by_player"
    # tick = "tick"
    # used_ender_eye = "used_ender_eye"
    # used_totem = "used_totem"
    # using_item = "using_item"
    # villager_trade = "villager_trade"
    # voluntary_exile = "voluntary_exile"
    # arbitrary_player_tick = "arbitrary_player_tick"
    # player_damaged = "player_damaged"
    # safely_harvest_honey = "safely_harvest_honey"


class ActionEvent(object):
    """行为事件"""
    AddItem = "add_item"
    CastEffect = "cast_effect"
    CastDamage = "cast_damage"
    TriggerEvent = "trigger_event"
    SendMessage = "send_message"
    RunCommand = "run_command"
    SpawnEntity = "spawn_entity"
    # Timeline = "timeline"
    # Repeater = "repeater"
    # CastExplode = "cast_explode"
    # AddDamageRate = "add_damage_rate"
    # DelDamageRate = "del_damage_taken"
    # DealDamageRate = "deal_damage_rate"
    # AddCureRate = "add_cure_rate"
    # ModifyAttr = "modify_attr"
    # TriggerEntityEvent = "trigger_entity_event"


class ActionFunc(object):
    """行为功能"""
    SetName = "set_name"
    SetLore = "set_lore"
    SetCount = "set_count"
    SetStorage = "set_storage"
    SetLootTable = "set_loot_table"
    AddEntityTag = "add_entity_tag"
    LimitCount = "limit_count"

    # AddTag = "add_tag"
    # ApplyBonus = "apply_bonus"
    # CopyName = "copy_name"
    # CopyNbt = "copy_nbt"
    # CopyState = "copy_state"
    # EnchantRandomly = "enchant_randomly"
    # EnchantWithLevels = "enchant_with_levels"
    # ExplorationMap = "exploration_map"
    # ExplosionDecay = "explosion_decay"
    # FurnaceSmelt = "furnace_smelt"
    # FillPlayerHead = "fill_player_head"
    # LootingEnchant = "looting_enchant"
    # SetAttributes = "set_attributes"
    # SetContents = "set_contents"
    # SetDamage = "set_damage"
    # SetEnchantments = "set_enchantments"
    # SetNbt = "set_nbt"
    # SetPotion = "set_potion"
    # SetStewEffect = "set_stew_effect"


class ActionCondition(object):
    """行为条件"""
    RandomChance = "random_chance"
    StorageCheck = "storage_check"
    EntityProperties = "entity_properties"
    BlockStateProperty = "block_state_property"
    LocationCheck = "location_check"


class ActionType(object):
    """行为类型"""
    Generic = "generic"
    Alternative = "alternative"
    Group = "group"
    Sequence = "sequence"
    Sample = "sample"
    # Tag = "tag"


class OperateType(object):
    """操作类型"""
    Always = "always"
    Equal = "equal"
    NotEqual = "not_equal"
    Less = "less"
    Greater = "greater"
    GreaterEqual = "greater_equal"
    LessEqual = "less_equal"
    In = "in"
    NotIn = "not_in"


class RangeType(object):
    """区间解析类型"""
    Constant = "constant"
    Binomial = "binomial"
    Uniform = "uniform"
    RandomInt = "random_int"
    # Score = "score"


class BaseOnType(object):
    """依赖类型"""
    Health = "health"
    MaxHealth = "max_health"
    Storage = "storage"
