# -*- coding:utf-8 -*-


from mod.common import minecraftEnum

from event import *


# 游戏枚举
class GameEnum(modConfig.ModEnum):
    """游戏枚举"""


# 游戏物品
class GameItem(modConfig.ModItem):
    """游戏物品"""
    apple = "minecraft:apple"
    diamond = "minecraft:diamond"
    iron_ingot = "minecraft:iron_ingot"

    # weapon
    bow = "minecraft:bow"
    crossbow = "minecraft:crossbow"

    # tool


# 游戏方块
class GameBlock(modConfig.ModBlock):
    """游戏方块"""
    air = "minecraft:air"
    fire = "minecraft:fire"
    leaves = "minecraft:leaves"

    chest = "minecraft:chest"
    barrel = "minecraft:barrel"
    shulker_box = "minecraft:shulker_box"

    barrier = "minecraft:barrier"

    gold_block = "minecraft:gold_block"


# 游戏实体
class GameEntity(modConfig.ModEntity):
    """游戏实体"""
    # 预设实体
    detector = "common:detector"
    projectile = "common:projectile"
    particle = "common:particle"

    # 原版实体
    player = "minecraft:player"  # 玩家

    # projectile
    snowball = "minecraft:snowball"  # 雪球
    fireworks_rocket = "minecraft:fireworks_rocket"  # 烟花
    lightning_bolt = "minecraft:lightning_bolt"  # 闪电

    # aggressive
    blaze = "minecraft:blaze"  # 烈焰人
    zombie = "minecraft:zombie"  # 僵尸
    creeper = "minecraft:creeper"  # 苦力怕
    drowned = "minecraft:drowned"  # 溺尸
    cave_spider = "minecraft:cave_spider"  # 洞穴蜘蛛
    elder_guardian = "minecraft:elder_guardian"
    endermite = "minecraft:endermite"  # 末影螨
    enderman = "minecraft:enderman"  # 末影人
    evoker = "minecraft:evoker"
    spider = "minecraft:spider"  # 蜘蛛
    ghast = "minecraft:ghast"  # 恶魂
    guardian = "minecraft:guardian"  # 守卫者
    husk = "minecraft:husk"  # 尸壳
    hoglin = "minecraft:hoglin"  # 猪灵
    zoglin = "minecraft:zoglin"  # 猪灵疣猪兽
    magma_cube = "minecraft:magma_cube"
    phantom = "minecraft:phantom"  # 幻翼
    pillager = "minecraft:pillager"  # 掠夺者
    shulker = "minecraft:shulker"  # 潜影贝
    silverfish = "minecraft:silverfish"  # 蠹虫
    skeleton = "minecraft:skeleton"  # 骷髅
    slime = "minecraft:slime"  # 史莱姆
    stray = "minecraft:stray"
    ravager = "minecraft:ravager"  # 掠夺兽
    wither = "minecraft:wither"
    vex = "minecraft:vex"
    vindicator = "minecraft:vindicator"
    witch = "minecraft:witch"  # 女巫
    wither_skeleton = "minecraft:wither_skeleton"
    zombie_villager = "minecraft:zombie_villager"
    piglin = "minecraft:piglin"
    piglin_brute = "minecraft:piglin_brute"
    skeleton_horse = "minecraft:skeleton_horse"
    zombified_piglin = "minecraft:zombified_piglin"
    illusioner = "minecraft:illusioner"

    # neutral
    bee = "minecraft:bee"
    snowman = "minecraft:snow_golem"  # 雪傀儡


# 游戏标签
class GameTag(modConfig.ModTag):
    """游戏标签"""
    Container = [
        GameBlock.chest,
        GameBlock.barrel,
        GameBlock.shulker_box,
    ]


# 游戏过滤器
class GameFilter(modConfig.ModFilter):
    """游戏过滤器"""
    Mob = {
        "all_of": [
            {
                "any_of": [
                    {
                        "subject": "other",
                        "test": "is_family",
                        "value": "mob"
                    },
                    {
                        "subject": "other",
                        "test": "is_family",
                        "value": "monster"
                    },
                    {
                        "subject": "other",
                        "test": "is_family",
                        "value": "player"
                    },
                    {
                        "subject": "other",
                        "test": "is_family",
                        "value": "panda"
                    },
                    {
                        "subject": "other",
                        "test": "is_family",
                        "value": "goat"
                    }
                ]
            },
            {
                "subject": "other",
                "test": "is_family",
                "operator": "!=",
                "value": "detector"
            },
            {
                "subject": "other",
                "test": "is_family",
                "operator": "!=",
                "value": "skill_entity"
            }
        ]
    }
    Monster = {
        "subject": "other",
        "test": "is_family",
        "value": "monster"
    }
    NonMonster = {
        "subject": "other",
        "test": "is_family",
        "operator": "!=",
        "value": "monster"
    }
    Player = {
        "subject": "other",
        "test": "is_family",
        "value": "player"
    }
    NonPlayer = {
        "subject": "other",
        "test": "is_family",
        "operator": "!=",
        "value": "player"
    }

    Treat_player = {
        "any_of": [
            {
                "subject": "other",
                "test": "is_family",
                "value": "player"
            }]}


# 游戏效果
class GameEffect(modConfig.ModEffect, minecraftEnum.EffectType):
    """游戏效果"""


# 游戏自定义属性
class GameAttr(modConfig.ModAttr):
    """游戏自定义属性"""
    # -----------------------------------------------------------------------------------
    """通用类型"""
    Name = "name"
    Exp = "exp"
    NextExp = "next_exp"
    Level = "level"
    Movement = "movement"
    # -----------------------------------------------------------------------------------
    """RPG类型"""
    Health = "health"
    MaxHealth = "max_health"
    HealthRegen = "health_regen"
    DamageDrop = "damage_drop"
    Mana = "mana"
    MaxMana = "max_mana"
    ManaRegen = "mana_regen"
    Stamina = "stamina"
    MaxStamina = "max_stamina"
    StaminaRegen = "stamina_regen"
    Attack = "attack"
    AttackRate = "attack_rate"
    Shield = "shield"
    ShieldRegen = "shield_regen"
    Crit = "crit"
    CritRate = "crit_rate"
    MagicAttack = "magic_attack"
    MagicAttackRate = "magic_attack_rate"
    MagicCrit = "magic_crit"
    MagicCritRate = "magic_crit_rate"
    # -----------------------------------------------------------------------------------
    """生存类型"""
    Thirst = "thirst"
    MaxThirst = "max_thirst"
    Duration = "duration"
    MaxDuration = "max_duration"
    # -----------------------------------------------------------------------------------


# 游戏迷雾
class GameFog(modConfig.ModFog):
    """游戏迷雾"""


# 游戏molang
class GameMolang(modConfig.ModMolang):
    """游戏molang"""
    # 预设molang
    VModState = "variable.mod_state"
    CustomPlayer = "query.mod.custom_player"
    CustomAttack = "query.mod.custom_attack"
    CustomSkill = "query.mod.custom_skill"


# 游戏维度
class GameDimension(modConfig.ModDimension):
    """游戏维度"""
    Overworld = 0
    Nether = 1
    End = 2


# 游戏规则
class GameRule(object):
    """游戏规则"""
    pvp = "pvp"  # 玩家伤害
    show_coordinates = "show_coordinates"  # 显示坐标
    fire_spreads = "fire_spreads"  # 火焰蔓延
    tnt_explodes = "tnt_explodes"  # tnt爆炸
    mob_loot = "mob_loot"  # 生物战利品
    natural_regeneration = "natural_regeneration"  # 自然生命恢复
    tile_drops = "tile_drops"  # 方块掉落
    immediate_respawn = "immediate_respawn"  # 立即重生
    # -----------------------------------------------------------------------------------
    enable = "enable"  # 是否开启作弊
    always_day = "always_day"  # 终为白日
    mob_griefing = "mob_griefing"  # 生物破坏方块
    keep_inventory = "keep_inventory"  # 保留物品栏
    weather_cycle = "weather_cycle"  # 天气更替
    mob_spawn = "mob_spawn"  # 生物生成
    entities_drop_loot = "entities_drop_loot"  # 实体掉落
    daylight_cycle = "daylight_cycle"  # 开启昼夜交替
    command_blocks_enabled = "command_blocks_enabled"  # 启用方块命令
    random_tick_speed = "random_tick_speed"  # 随机方块tick速度


# 游戏系统基类
class GameSystem(object):
    """系统基类"""
    __mVersion__ = 4

    def __init__(self, *args, **kwargs):
        self.defaultEvent = {}
        self.serverEvent = {}
        self.clientEvent = {}
        self.ConfigEvent()
        if not kwargs.get("manual_listen"):
            self.OnInit()

    # -----------------------------------------------------------------------------------

    def ConfigEvent(self):
        """配置事件监听"""

    def OnInit(self):
        """启动回调"""
        self._InitEvent()

    def OnDestroy(self):
        """销毁回调"""
        self._DestroyEvent()

    # -----------------------------------------------------------------------------------

    def _InitEvent(self):
        """初始化监听"""

    def _DestroyEvent(self):
        """反监听"""
        del self.defaultEvent
        del self.serverEvent
        del self.clientEvent
