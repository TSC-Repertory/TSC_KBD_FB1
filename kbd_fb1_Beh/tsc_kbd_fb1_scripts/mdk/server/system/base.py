# -*- coding:utf-8 -*-


import weakref

from ..entity import *
from ..item import *
from ...common.system.base import *
from ...common.utils.misc import Misc
from ...loader import MDKConfig


class ServerModuleExtend(object):
    """服务端模块拓展"""
    __mVersion__ = 1

    _module_system = None

    @property
    def ModuleSystem(self):
        # type: () -> MDKConfig.GetModuleServerSystemCls()
        if ServerModuleExtend._module_system:
            return ServerModuleExtend._module_system
        ServerModuleExtend._module_system = weakref.proxy(MDKConfig.GetModuleServer())
        return ServerModuleExtend._module_system

    _attr_module = None

    @property
    def AttrModule(self):
        # type: () -> MDKConfig.GetPresetModule().AttrModuleServer
        if ServerModuleExtend._attr_module:
            return ServerModuleExtend._attr_module
        module = self.ModuleSystem.GetModule(MDKConfig.GetPresetModule().AttrModuleServer.GetId())
        if not module:
            return None
        ServerModuleExtend._attr_module = weakref.proxy(module)
        return ServerModuleExtend._attr_module

    _effect_module = None

    @property
    def EffectModule(self):
        # type: () -> MDKConfig.GetPresetModule().EffectModuleServer
        if ServerModuleExtend._effect_module:
            return ServerModuleExtend._effect_module
        module = self.ModuleSystem.GetModule(MDKConfig.GetPresetModule().EffectModuleServer.GetId())
        if not module:
            return None
        ServerModuleExtend._effect_module = weakref.proxy(module)
        return ServerModuleExtend._effect_module

    _particle_module = None

    @property
    def ParticleModule(self):
        # type: () -> MDKConfig.GetPresetModule().ParticleModuleServer
        if ServerModuleExtend._particle_module:
            return ServerModuleExtend._particle_module
        module = self.ModuleSystem.GetModule(MDKConfig.GetPresetModule().ParticleModuleServer.GetId())
        if not module:
            return None
        ServerModuleExtend._particle_module = weakref.proxy(module)
        return ServerModuleExtend._particle_module

    _property_module = None

    @property
    def PropertyModule(self):
        # type: () -> MDKConfig.GetPresetModule().PropertyModuleServer
        if ServerModuleExtend._property_module:
            return ServerModuleExtend._property_module
        module = self.ModuleSystem.GetModule(MDKConfig.GetPresetModule().PropertyModuleServer.GetId())
        if not module:
            return None
        ServerModuleExtend._property_module = weakref.proxy(module)
        return ServerModuleExtend._property_module

    _quest_module = None

    @property
    def QuestModule(self):
        # type: () -> MDKConfig.GetPresetModule().QuestModuleServer
        if ServerModuleExtend._quest_module:
            return ServerModuleExtend._quest_module
        module = self.ModuleSystem.GetModule(MDKConfig.GetPresetModule().QuestModuleServer.GetId())
        if not module:
            return None
        ServerModuleExtend._quest_module = weakref.proxy(module)
        return ServerModuleExtend._quest_module


class ServerBaseSystem(GameSystem, ServerModuleExtend, ServerRecall):
    """服务端系统基类"""
    __mVersion__ = 15

    def __init__(self, system, *args, **kwargs):
        self.RawEntity = RawEntity
        self.PlayerEntity = PlayerEntity
        self.ProjectileEntity = ProjectileEntity
        self.ParticleEntity = ParticleEntity
        self.Item = ServerItem
        self.Inventory = ServerInventoryMgr

        self.__namespace = serverApi.GetEngineNamespace()
        self.__system_name = serverApi.GetEngineSystemName()

        self.system = system  # type: serverApi.GetServerSystemCls()

        level_id = serverApi.GetLevelId()
        self.comp_factory = serverApi.GetEngineCompFactory()
        self.game_comp = self.comp_factory.CreateGame(level_id)
        self.block_comp = self.comp_factory.CreateBlockInfo(level_id)
        self.command_comp = self.comp_factory.CreateCommand(level_id)
        self.feature_comp = self.comp_factory.CreateFeature(level_id)
        self.weather_comp = self.comp_factory.CreateWeather(level_id)
        self.achieve_comp = self.comp_factory.CreateAchievement(level_id)
        self.chunk_comp = self.comp_factory.CreateChunkSource(level_id)

        super(ServerBaseSystem, self).__init__(*args, **kwargs)

    def OnDestroy(self):
        super(ServerBaseSystem, self).OnDestroy()
        del self.system

    def _InitEvent(self):
        self.BatchListenDefault(self.defaultEvent)
        self.BatchListenBaseServer(self.serverEvent)
        self.BatchListenBaseClient(self.clientEvent)
        super(ServerBaseSystem, self)._InitEvent()

    def _DestroyEvent(self):
        self.BatchUnListenDefault(self.defaultEvent)
        self.BatchUnListenBaseServer(self.serverEvent)
        self.BatchUnListenBaseClient(self.clientEvent)
        super(ServerBaseSystem, self)._DestroyEvent()

    # -----------------------------------------------------------------------------------

    def KillEntity(self, targetId):
        # type: (str) -> None
        """使用杀死的方式清除实体"""
        self.game_comp.KillEntity(targetId)

    def IsPvpMode(self):
        # type: () -> bool
        """是否设置pvp模式"""
        rule = self.game_comp.GetGameRulesInfoServer()
        return rule["option_info"]["pvp"]

    def SetGlobalKeepInventory(self, active):
        """设置全局死亡不掉落"""
        rule = self.game_comp.GetGameRulesInfoServer()
        rule["cheat_info"]["keep_inventory"] = active
        self.game_comp.SetGameRulesInfoServer(rule)

    # -----------------------------------------------------------------------------------

    """规则相关"""

    def GetGameRule(self, queryKey):
        # type: (str) -> any
        """
        查询游戏规则\n
        - option_info
            - pvp: bool 玩家伤害
            - show_coordinates: bool 显示坐标
            - fire_spreads: bool 火焰蔓延
            - tnt_explodes: bool tnt爆炸
            - mob_loot: bool 生物战利品
            - natural_regeneration: bool 自然生命恢复
            - tile_drops: bool 方块掉落
            - immediate_respawn: bool   立即重生
        - cheat_info
            - enable: bool 是否开启作弊
            - always_day: bool 终为白日
            - mob_griefing: bool 生物破坏方块
            - keep_inventory: bool 保留物品栏
            - weather_cycle: bool 天气更替
            - mob_spawn: bool 生物生成
            - entities_drop_loot: bool 实体掉落
            - daylight_cycle: bool 开启昼夜交替
            - command_blocks_enabled: bool 启用方块命令
            - random_tick_speed: int 随机方块tick速度
        """
        config = self.game_comp.GetGameRulesInfoServer()
        rules = {}
        rules.update(config["option_info"])
        rules.update(config["cheat_info"])
        return rules.get(queryKey)

    def SetPvpMode(self, active):
        """设置Pvp模式"""
        rule = self.game_comp.GetGameRulesInfoServer()
        rule["option_info"]["pvp"] = active
        self.game_comp.SetGameRulesInfoServer(rule)

    def SetDisableDropItem(self, active):
        """设置禁止丢弃物品"""
        self.game_comp.SetDisableDropItem(active)

    def SetDisableContainers(self, active):
        """
        禁止所有容器界面的打开\n
        - 包括玩家背包
        - 各种包含背包界面的容器方块如工作台与箱子
        - 以及包含背包界面的实体交互如马背包与村民交易
        """
        self.game_comp.SetDisableContainers(active)

    # -----------------------------------------------------------------------------------

    @staticmethod
    def IsInArea(minPos, maxPos, pos):
        # type: (tuple, tuple, tuple) -> bool
        """是否在区域内"""
        for i in xrange(3):
            if not (minPos[i] <= pos[i] <= maxPos[i]):
                return False
        return True

    # -----------------------------------------------------------------------------------

    def SetAllPlayerTitleDisplay(self, title, subtitle=None, action=None):
        # type: (str, str, str) -> None
        """指令方式显示所有玩家的标题"""
        player_id = serverApi.GetPlayerList()[0]
        self.command_comp.SetCommand("/title @a title %s" % title, player_id)
        if subtitle:
            self.command_comp.SetCommand("/title @a subtitle %s" % subtitle, player_id)
        if action:
            self.command_comp.SetCommand("/title @a actionbar %s" % action, player_id)

    def SetPlayerTitleDisplay(self, player_id, title, subtitle=None, action=None):
        # type: (str, str, str, str) -> None
        """指令方式显示玩家的标题"""
        self.command_comp.SetCommand("/title @a title %s" % title, player_id)
        if subtitle:
            self.command_comp.SetCommand("/title @a subtitle %s" % subtitle, player_id)
        if action:
            self.command_comp.SetCommand("/title @a actionbar %s" % action, player_id)

    def SetWorldChat(self, msg):
        # type: (str) -> None
        """设置世界消息"""
        self.game_comp.SetNotifyMsg(msg)
        if self.ModuleSystem.HasModule("chat"):
            self.BroadcastToAllClient("ModuleRequestDisplayChatEvent", {"context": msg})

    def SetCameraShake(self, player_id, intensity, seconds):
        # type: (str, float, float) -> None
        """指令的相机震动"""
        self.command_comp.SetCommand("/camerashake add @s %s %s" % (intensity, seconds), player_id)

    # -----------------------------------------------------------------------------------

    def PlayMusic(self, player_id, path):
        self.command_comp.SetCommand("/playsound %s @s ~~~ 1 1 1" % path, player_id)

    def StopMusic(self, player_id, path):
        self.command_comp.SetCommand("/stopsound @s %s" % path, player_id)

    def PlayParticle(self, particle, pos):
        # type: (str, tuple) -> None
        """播放原版粒子"""
        player_id = serverApi.GetPlayerList()[0]
        self.command_comp.SetCommand("/particle %s %s %s %s" % (particle, pos[0], pos[1], pos[2]), player_id)

    # -----------------------------------------------------------------------------------

    def GetEngineTypeStr(self, entityId):
        """获取实体类型"""
        return self.comp_factory.CreateEngineType(entityId).GetEngineTypeStr()

    def GetSquareEntities(self, pos, dim_id, **kwargs):
        # type: (tuple, int, any) -> list
        """获取方块矩形区域生物列表"""
        radius = kwargs.get("radius")
        if radius:
            radius = max(1, radius)
            start = Misc.GetPosModify(pos, (-radius, -radius, -radius))
            end = Misc.GetPosModify(pos, (radius, radius, radius))
            return self.game_comp.GetEntitiesInSquareArea(None, start, end, dim_id)
        # -----------------------------------------------------------------------------------
        start = kwargs.get("offset1", (0, 0, 0))
        end = kwargs.get("offset2", (0, 0, 0))
        start = Misc.GetPosModify(pos, start)
        end = Misc.GetPosModify(pos, end)
        return self.game_comp.GetEntitiesInSquareArea(None, start, end, dim_id)

    def GetLevelStorage(self, key):
        # type: (str) -> dict
        """获得模组的世界数据"""
        data_comp = self.comp_factory.CreateExtraData(serverApi.GetLevelId())
        if data_comp.GetExtraData(key) is None:
            data_comp.SetExtraData(key, {})
        storage = data_comp.GetExtraData(key)
        return storage

    def ClearLevelStorage(self, key):
        # type: (str) -> bool
        """清除世界数据"""
        data_comp = self.comp_factory.CreateExtraData(serverApi.GetLevelId())
        return data_comp.CleanExtraData(key)

    def SetLevelStorage(self, key, storage):
        # type: (str, dict) -> None
        """设置模组的世界数据"""
        data_comp = self.comp_factory.CreateExtraData(serverApi.GetLevelId())
        data_comp.SetExtraData(key, storage)

    def GetLevelDataByKey(self, data_key, storage_key):
        # type: (str, str) -> any
        """根据键值获取某个自定义世界数据"""
        storage = self.GetLevelStorage(data_key)
        return storage.get(storage_key)

    # -----------------------------------------------------------------------------------

    def BroadcastEvent(self, event, pack):
        """服务端广播事件"""
        self.system.BroadcastEvent(event, pack)

    def BroadcastToAllClient(self, event, pack):
        """广播客户端事件"""
        self.system.BroadcastToAllClient(event, pack)

    def NotifyToClient(self, playerId, event, pack):
        """通知客户端事件"""
        self.system.NotifyToClient(playerId, event, pack)

    def NotifyToMultiClients(self, player_list, event, pack):
        """通知多个客户端事件"""
        system = self.system
        for target in list(player_list):
            system.NotifyToClient(target, event, pack)

    # -----------------------------------------------------------------------------------

    def BatchListenDefault(self, event_map):
        # type: (any, dict) -> None
        for event, recall in event_map.iteritems():
            if isinstance(recall, tuple):
                self.ListenDefaultEvent(event, recall[0], recall[1])
            else:
                self.ListenDefaultEvent(event, recall)

    def BatchListenBaseServer(self, event_map):
        # type: (any, dict) -> None
        for event, recall in event_map.iteritems():
            if isinstance(recall, tuple):
                self.ListenBaseServer(event, recall[0], recall[1])
            else:
                self.ListenBaseServer(event, recall)

    def BatchListenBaseClient(self, event_map):
        # type: (any, dict) -> None
        for event, recall in event_map.iteritems():
            if isinstance(recall, tuple):
                self.ListenBaseClient(event, recall[0], recall[1])
            else:
                self.ListenBaseClient(event, recall)

    def BatchUnListenDefault(self, event_map):
        # type: (any, dict) -> None
        for event, recall in event_map.iteritems():
            if isinstance(recall, tuple):
                self.UnListenDefaultEvent(event, recall[0], recall[1])
            else:
                self.UnListenDefaultEvent(event, recall)

    def BatchUnListenBaseServer(self, event_map):
        # type: (any, dict) -> None
        for event, recall in event_map.iteritems():
            if isinstance(recall, tuple):
                self.UnListenBaseServer(event, recall[0], recall[1])
            else:
                self.UnListenBaseServer(event, recall)

    def BatchUnListenBaseClient(self, event_map):
        # type: (any, dict) -> None
        for event, recall in event_map.iteritems():
            if isinstance(recall, tuple):
                self.UnListenBaseClient(event, recall[0], recall[1])
            else:
                self.UnListenBaseClient(event, recall)

    # -----------------------------------------------------------------------------------

    def ListenDefaultEvent(self, event, recall, priority=0):
        self.system.ListenForEvent(self.__namespace, self.__system_name, event, recall.im_self, recall, priority)

    def ListenBaseServer(self, event, recall, priority=0):
        self.system.ListenForEvent(MDKConfig.ModuleNamespace, MDKConfig.ServerSysName, event, recall.im_self, recall,
                                   priority)

    def ListenBaseClient(self, event, recall, priority=0):
        self.system.ListenForEvent(MDKConfig.ModuleNamespace, MDKConfig.ClientSysName, event, recall.im_self, recall,
                                   priority)

    def UnListenDefaultEvent(self, event, recall, priority=0):
        self.system.UnListenForEvent(self.__namespace, self.__system_name, event, recall.im_self, recall, priority)

    def UnListenBaseServer(self, event, recall, priority=0):
        self.system.UnListenForEvent(MDKConfig.ModuleNamespace, MDKConfig.ServerSysName, event, recall.im_self, recall,
                                     priority)

    def UnListenBaseClient(self, event, recall, priority=0):
        self.system.UnListenForEvent(MDKConfig.ModuleNamespace, MDKConfig.ClientSysName, event, recall.im_self, recall,
                                     priority)

    # -----------------------------------------------------------------------------------

    def StartCoroutine(self, coroutine, recall=None):
        return self.ModuleSystem.StartCoroutine(coroutine, recall)

    def StartCoroutineLine(self, config):
        return self.ModuleSystem.StartCoroutineLine(config)

    def StopCoroutine(self, coroutine, isSafe=False):
        return self.ModuleSystem.StopCoroutine(coroutine, isSafe)

    def GetCoroutine(self, coroutine):
        return self.ModuleSystem.GetCoroutine(coroutine)

    def DelayTickFunc(self, tick, func):
        # type: (int, any) -> any
        """延迟刻执行"""
        if not callable(func):
            return

        def active():
            yield tick
            func()

        return self.StartCoroutine(active)

    # -----------------------------------------------------------------------------------

    def RegisterFeatureListener(self, featureList):
        # type: (list) -> None
        """添加结构对PlaceNeteaseStructureFeatureEvent事件的脚本层监听"""
        for structureName in featureList:
            self.feature_comp.AddNeteaseFeatureWhiteList(structureName)

    def RegisterBlockUseListener(self, blocks):
        # type: (list) -> None
        """
        增加block_name方块对ServerBlockUseEvent事件的脚本层监听\n
        - block_name: str 方块名称，格式：namespace:name:auxvalue，其中namespace:name:*匹配所有的auxvalue
        """
        comp = self.comp_factory.CreateBlockUseEventWhiteList(serverApi.GetLevelId())
        for block_name in blocks:
            comp.AddBlockItemListenForUseEvent(block_name)

    def UnRegisterBlockUseListener(self, blocks):
        # type: (list) -> None
        """移除block_name方块对ServerBlockUseEvent事件的脚本层监听"""
        comp = self.comp_factory.CreateBlockUseEventWhiteList(serverApi.GetLevelId())
        for block_name in blocks:
            comp.RemoveBlockItemListenForUseEvent(block_name)

    def UnRegisterAllBlockUseListener(self):
        # type: () -> bool
        """
        清空所有已添加方块对ServerBlockUseEvent事件的脚本层监听\n
        - 尽量不用，避免干扰其他模组
        """
        comp = self.comp_factory.CreateBlockUseEventWhiteList(serverApi.GetLevelId())
        return comp.ClearAllListenForBlockUseEventItems()

    # -----------------------------------------------------------------------------------

    @staticmethod
    def AddEntity(engineType, pos, dim, rot=(0, 0)):
        # type: (str, tuple, int, tuple) -> str
        """创建实体"""
        return RawEntity.CreateRaw(engineType, pos, dim, rot)

    def AddProjectile(self, engineType, position=None, direction=None, owner_id=None, **kwargs):
        """
        添加抛射物\n
        - position: tuple(float,float,float)	初始位置
        - direction: tuple(float,float,float)	初始朝向
        - power: float	投掷的力量值
        - gravity: float	抛射物重力因子，默认为json配置中的值
        - damage: float	抛射物伤害值，默认为json配置中的值
        - targetId: str	抛射物目标（指定了target之后，会和潜影贝生物发射的跟踪导弹的那个投掷物是一个效果），默认不指定
        - isDamageOwner: bool	对创建者是否造成伤害，默认不造成伤害
        """
        if not position:
            print "[error]", "抛射物创建失败：缺少位置参数<position>"
            return None
        if not direction:
            print "[error]", "抛射物创建失败：缺少朝向参数<direction>"
            return
        # -----------------------------------------------------------------------------------
        """抛射物配置"""
        param = {"position": position, "direction": direction}
        # -----------------------------------------------------------------------------------
        """抛射力量"""
        power = kwargs.get("power")
        if power is not None:
            param["power"] = power
        # -----------------------------------------------------------------------------------
        """抛射重力"""
        gravity = kwargs.get("gravity")
        if gravity is not None:
            param["gravity"] = gravity
        # -----------------------------------------------------------------------------------
        """抛射伤害"""
        damage = kwargs.get("damage")
        if damage is not None:
            param["damage"] = damage
        # -----------------------------------------------------------------------------------
        if not owner_id and hasattr(self, "id"):
            owner_id = getattr(self, "id")
        else:
            owner_id = serverApi.GetLevelId()
        # -----------------------------------------------------------------------------------
        comp = self.comp_factory.CreateProjectile(serverApi.GetLevelId())
        entity_id = comp.CreateProjectileEntity(owner_id, engineType, param)
        return ProjectileEntity(entity_id)

    def AddExplosion(self, pos, radius=1, sourceId=None, playerId=None, fire=None, breaks=None):
        # type: (tuple, int, str, str, bool, bool) -> bool
        """
        添加爆炸\n
        默认随游戏规则爆炸和着火
        """
        comp = self.comp_factory.CreateExplosion(serverApi.GetLevelId())
        rule = self.game_comp.GetGameRulesInfoServer()  # type: dict
        if fire is None:
            fire = rule["option_info"][GameRule.fire_spreads]
        if breaks is None:
            breaks = rule["cheat_info"][GameRule.mob_griefing]
        # -----------------------------------------------------------------------------------
        return comp.CreateExplosion(pos, radius, fire, breaks, sourceId, playerId)
