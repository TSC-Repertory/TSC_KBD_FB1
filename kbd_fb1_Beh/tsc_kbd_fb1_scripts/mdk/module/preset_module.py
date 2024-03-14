# -*- coding:utf-8 -*-


from attribute import *
from block import *
from buff import *
from camera import *
from chat import *
from combo import *
from debug import *
from dialog import *
from dungeon import *
from effect import *
from indicator import *
from item import *
from loot import *
from mob import *
from move import *
from music import *
from particle import *
from predicate import *
from projectile import *
from property import *
from quest import *
from render import *
from rpc import *
from skill import *
from tag import *
from world import *

assert AttrModuleServer
assert AttrModuleClient
AttrModuleId = AttrModuleServer.__identifier__

assert BlockModuleServer
assert BlockModuleClient
BlockModuleId = BlockModuleServer.__identifier__

assert BuffModuleServer
assert BuffModuleClient
BuffModuleId = BuffModuleServer.__identifier__

assert CameraModuleServer
assert CameraModuleClient
CameraModuleId = CameraModuleServer.__identifier__

assert ChatModuleServer
assert ChatModuleClient
ChatModuleId = ChatModuleServer.__identifier__

assert ComboModuleServer
assert ComboModuleClient
ComboModuleId = ComboModuleServer.__identifier__

assert DebugModuleServer
assert DebugModuleClient
DebugModuleId = DebugModuleServer.__identifier__

assert DialogModuleServer
assert DialogModuleClient
DialogModuleId = DialogModuleServer.__identifier__

assert DungeonModuleServer
assert DungeonModuleClient
DungeonModuleId = DungeonModuleServer.__identifier__

assert EffectModuleServer
EffectModuleId = EffectModuleServer.__identifier__

assert IndicatorModuleServer
assert IndicatorModuleClient
IndicatorModuleId = IndicatorModuleServer.__identifier__

assert ItemModuleServer
ItemModuleId = ItemModuleServer.__identifier__
assert ItemFoodConsumeModuleServer
ItemFoodConsumeModuleId = ItemFoodConsumeModuleServer.__identifier__
assert ItemRecipeCraftModuleServer
ItemRecipeCraftModuleId = ItemRecipeCraftModuleServer.__identifier__

assert LootModuleServer
LootModuleId = LootModuleServer.__identifier__

assert MobModuleServer
MobModuleId = MobModuleServer.__identifier__

assert MoveModuleServer
assert MoveModuleClient
MoveModuleId = MoveModuleServer.__identifier__

assert MusicModuleClient
MusicModuleId = MusicModuleClient.__identifier__

assert ParticleModuleServer
assert ParticleModuleClient
ParticleModuleId = ParticleModuleServer.__identifier__

assert PredicateModuleServer
assert PredicateModuleClient
PredicateModuleId = PredicateModuleServer.__identifier__

assert ProjectileModuleServer
ProjectileModuleId = ProjectileModuleServer.__identifier__

assert PropertyModuleServer
assert PropertyModuleClient
PropertyModuleId = PropertyModuleServer.__identifier__

assert QuestModuleServer
assert QuestModuleClient
QuestModuleId = QuestModuleServer.__identifier__

assert RenderModuleServer
assert RenderModuleClient
RenderModuleId = RenderModuleServer.__identifier__

assert RpcModuleServer
assert RpcModuleClient

assert SkillModuleServer
assert SkillModuleClient
SkillModuleId = SkillModuleServer.__identifier__

assert TagModuleServer
assert TagModuleClient
TagModuleId = TagModuleServer.__identifier__

assert WorldModuleServer
WorldModuleId = WorldModuleServer.__identifier__
