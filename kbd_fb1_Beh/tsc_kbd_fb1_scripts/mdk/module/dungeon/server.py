# -*- coding:utf-8 -*-


from const import *
from parts.base import ModuleDungeonBase
from ..system.base import *
from ...server.entity import RawEntity


class DungeonModuleServer(ModuleServerBase):
    """副本模块服务端"""
    __mVersion__ = 5
    __identifier__ = ModuleEnum.identifier

    def __init__(self):
        super(DungeonModuleServer, self).__init__()
        self.flag_finished_load = False
        self.dirty_player = set()

        # 玩家维度缓存
        self.player_storage = {}  # player_id: dict
        # 副本实例
        self.dungeon_storage = {}  # dungeon_id: dungeon_ins
        # 副本激活集合
        self.dungeon_active = set()  # dungeon_id
        # 副本id实例对应
        self.dim_ins_storage = {}  # dim_id: {dungeon_id, }

        # 维度类对应
        self.dungeon_cls = {}  # dim_id: {dungeon_cls, }
        # 防破坏维度
        self.dungeon_ban_destroy = set()  # dim_id

    def OnDestroy(self):
        for dungeon in self.dungeon_storage.values():
            dungeon.OnDestroy()
        del self.dungeon_storage
        del self.dungeon_cls
        self.ModuleSystem.UnRegisterUpdateSecond(self.OnUpdateSecond)
        super(DungeonModuleServer, self).OnDestroy()

    def ConfigEvent(self):
        super(DungeonModuleServer, self).ConfigEvent()
        self.defaultEvent.update({
            ServerEvent.PlayerIntendLeaveServerEvent: self.PlayerIntendLeaveServerEvent,
            ServerEvent.PlayerRespawnFinishServerEvent: self.PlayerRespawnFinishServerEvent,
            ServerEvent.ClientLoadAddonsFinishServerEvent: self.ClientLoadAddonsFinishServerEvent,
            ServerEvent.DimensionChangeFinishServerEvent: self.DimensionChangeFinishServerEvent,
            ServerEvent.EntityChangeDimensionServerEvent: self.EntityChangeDimensionServerEvent,
            ServerEvent.ExplosionServerEvent: self.ExplosionServerEvent,
            ServerEvent.ServerEntityTryPlaceBlockEvent: self.ServerEntityTryPlaceBlockEvent,
            ServerEvent.ServerPlayerTryDestroyBlockEvent: self.ServerPlayerTryDestroyBlockEvent,
        })
        self.serverEvent.update({
            ServerEvent.ServerModuleFinishedLoadEvent: self.ServerModuleFinishedLoadEvent,
        })

    def _SetDungeonDimensionConfig(self, dimId):
        # type: (int) -> None
        """
        设置副本维度配置\n
        默认: \n
        - 使用维度独立天气\n
        - 关闭天气循环\n
        - 不下雨\n
        - 不雷雨\n
        """
        # 设置不下雨
        weatherComp = self.comp_factory.CreateWeather(serverApi.GetLevelId())
        weatherComp.SetDimensionUseLocalWeather(dimId, True)
        weatherComp.SetDimensionLocalDoWeatherCycle(dimId, False)
        weatherComp.SetDimensionLocalRain(dimId, 0, 0)
        weatherComp.SetDimensionLocalThunder(dimId, 0, 0)
        # 设置永远白天
        dimComp = self.comp_factory.CreateDimension(serverApi.GetLevelId())
        dimComp.SetUseLocalTime(dimId, True)
        dimComp.SetLocalDoDayNightCycle(dimId, False)
        dimComp.SetLocalTimeOfDay(dimId, 6000)

    # -----------------------------------------------------------------------------------

    def RegisterDungeonClass(self, dim_id, dim_cls, init=False):
        """注册副本类"""
        if dim_id not in self.dungeon_cls:
            self.dungeon_cls[dim_id] = set()
        class_set = self.dungeon_cls[dim_id]  # type: set
        class_set.add(dim_cls)
        if init:
            dungeon_ins = dim_cls(dim_id)
            self.AddDungeonIns(dungeon_ins)
            self.ActivateDungeonIns(id(dungeon_ins))

    def GetPlayerStorage(self, player_id):
        # type: (str) -> dict
        """获得玩家的维度缓存"""
        if player_id not in self.player_storage:
            self.player_storage[player_id] = {
                "pre_dim": RawEntity.GetDim(player_id),
                "last_dim": None,
                "last_dim_pos": {}
            }
        return self.player_storage[player_id]

    def RegisterBanDestroyDim(self, dim_id):
        # type: (str) -> None
        """注册禁止破坏维度"""
        self.dungeon_ban_destroy.add(dim_id)

    def UnRegisterBanDestroyDim(self, dim_id):
        # type: (str) -> None
        """反注册禁止破坏维度"""
        self.dungeon_ban_destroy.discard(dim_id)

    # -----------------------------------------------------------------------------------

    def OnUpdateSecond(self):
        """
        秒更新事件\n
        - 更新所有激活状态的副本
        """
        for dungeon_id in self.dungeon_active:
            dungeon_ins = self.GetDungeonIns(dungeon_id)
            dungeon_ins.OnUpdateSecond()

    def OnAddPlayerToDungeon(self, player_id, dim_id):
        # type: (str, int) -> None
        """添加玩家到副本"""
        dim_ins_storage = self.dim_ins_storage.get(dim_id)  # type: set
        if not dim_ins_storage:
            for dungeon_cls in list(self.dungeon_cls[dim_id]):
                dungeon_ins = dungeon_cls(dim_id)  # type: ModuleDungeonBase
                dungeon_ins.AddPlayer(player_id)
                self.AddDungeonIns(dungeon_ins)
                self.ActivateDungeonIns(id(dungeon_ins))
            return
        for dungeon_id in list(dim_ins_storage):
            dungeon_ins = self.GetDungeonIns(dungeon_id)  # type: ModuleDungeonBase
            dungeon_ins.AddPlayer(player_id)
            self.ActivateDungeonIns(id(dungeon_ins))

    def OnDelPlayerFromDungeon(self, player_id, dim_id):
        # type: (str, int) -> None
        """从副本删除玩家"""
        dim_ins_storage = self.dim_ins_storage.get(dim_id)  # type: set
        if not dim_ins_storage:
            return
        for dungeon_id in list(dim_ins_storage):
            dungeon_ins = self.GetDungeonIns(dungeon_id)  # type: ModuleDungeonBase
            dungeon_ins.DelPlayer(player_id)

    # -----------------------------------------------------------------------------------

    """副本相关"""

    def AddDungeonIns(self, dungeon_ins):
        # type: (ModuleDungeonBase) -> None
        """增加副本实例"""
        dungeon_id = id(dungeon_ins)
        self.dungeon_storage[dungeon_id] = dungeon_ins
        dim_id = dungeon_ins.id
        if dim_id not in self.dim_ins_storage:
            self.dim_ins_storage[dim_id] = set()
        dim_ins_storage = self.dim_ins_storage[dim_id]  # type: set
        dim_ins_storage.add(dungeon_id)

    def DelDungeonIns(self, dungeon_id):
        # type: (int) -> bool
        """删除实例"""
        self.dungeon_active.discard(dungeon_id)
        if dungeon_id not in self.dungeon_storage:
            return False
        dungeon_ins = self.dungeon_storage.pop(dungeon_id, None)  # type: ModuleDungeonBase
        if not dungeon_ins:
            return False
        dim_id = dungeon_ins.id
        dungeon_ins_storage = self.dim_ins_storage.get(dim_id)  # type: set
        dungeon_ins_storage.discard(dungeon_id)
        if not dungeon_ins_storage:
            self.dim_ins_storage.pop(dim_id, None)
        dungeon_ins.OnDestroy()

    def GetDungeonIns(self, dungeon_id):
        """获得副本实例"""
        dungeon_ins = self.dungeon_storage.get(dungeon_id)
        if not dungeon_ins:
            print "[warn]", "Invalid dungeon id: %s" % dungeon_id
            return None
        return dungeon_ins

    def ActivateDungeonIns(self, dungeon_id):
        # type: (int) -> bool
        """
        激活副本\n
        - 启动每秒更新
        """
        if dungeon_id not in self.dungeon_storage:
            return False
        self.dungeon_active.add(dungeon_id)
        return True

    def DeactivateDungeonIns(self, dungeon_id):
        # type: (int) -> bool
        """停止更新副本"""
        if dungeon_id not in self.dungeon_storage:
            return False
        self.dungeon_active.discard(dungeon_id)
        return True

    # -----------------------------------------------------------------------------------

    """事件相关"""

    # 检测玩家维度切换对副本实例的玩家管理
    def DimensionChangeFinishServerEvent(self, args):
        player_id = args.get("playerId")
        from_dim = args.get("fromDimensionId")
        to_dim = args.get("toDimensionId")
        # -----------------------------------------------------------------------------------
        storage = self.GetPlayerStorage(player_id)
        storage["pre_dim"] = to_dim
        # -----------------------------------------------------------------------------------
        """检测增加玩家"""
        if to_dim in self.dungeon_cls.keys():
            self.OnAddPlayerToDungeon(player_id, to_dim)
        # -----------------------------------------------------------------------------------
        """检测从关卡维度切出其他维度"""
        if from_dim in self.dungeon_cls.keys():
            self.OnDelPlayerFromDungeon(player_id, from_dim)

    # 用于玩家登录时在维度副本的处理
    def ClientLoadAddonsFinishServerEvent(self, args):
        player_id = args.get("playerId")
        dim_id = RawEntity.GetDim(player_id)
        storage = self.GetPlayerStorage(player_id)
        storage["pre_dim"] = dim_id
        if dim_id in self.dungeon_cls:
            self.OnAddPlayerToDungeon(player_id, dim_id)

    # 用于玩家重生时在维度副本的处理
    def PlayerRespawnFinishServerEvent(self, args):
        player_id = args.get("playerId")
        dim_id = RawEntity.GetDim(player_id)
        dim_ins_storage = self.dim_ins_storage.get(dim_id)  # type: set
        if dim_ins_storage:
            for dungeon_id in list(dim_ins_storage):
                dungeon_ins = self.GetDungeonIns(dungeon_id)  # type: ModuleDungeonBase
                dungeon_ins.OnPlayerRespawnFinished(player_id)

    # 玩家离开副本
    def PlayerIntendLeaveServerEvent(self, args):
        player_id = args.get("playerId")
        dim_id = RawEntity.GetDim(player_id)
        self.OnDelPlayerFromDungeon(player_id, dim_id)
        self.player_storage.pop(player_id, None)

    # 玩家从配置维度切换到关卡维度时保存切换前的坐标，用于从副本切回配置维度时能回到原位置
    def EntityChangeDimensionServerEvent(self, args):
        entity_id = args.get("entityId")
        from_dim = args.get("fromDimensionId")
        to_dim = args.get("toDimensionId")
        if not RawEntity.IsPlayer(entity_id) or from_dim == to_dim:
            return

        from_pos = (args["fromX"], args["fromY"], args["fromZ"])

        storage = self.GetPlayerStorage(entity_id)
        storage["dim_pos"][from_dim] = from_pos
        storage["last_dim"] = from_dim

    # 防止副本方块爆炸
    def ExplosionServerEvent(self, args):
        dim_id = args.get("dimensionId")
        if dim_id in self.dungeon_ban_destroy:
            for posList in args["blocks"]:
                posList[-1] = True

    # 防止副本方块放置
    def ServerEntityTryPlaceBlockEvent(self, args):
        dim_id = args.get("dimensionId")
        if dim_id in self.dungeon_ban_destroy:
            args["cancel"] = True

    # 防止副本方块破坏
    def ServerPlayerTryDestroyBlockEvent(self, args):
        dim_id = args.get("dimensionId")
        if dim_id in self.dungeon_ban_destroy:
            args["cancel"] = True

    def ServerModuleFinishedLoadEvent(self, _):
        def active():
            if not self.dungeon_cls:
                print "[warn]", "empty dungeon class map! destroying dungeon module server."
                self.ModuleSystem.DelModule(ModuleEnum.identifier)
            else:
                self.flag_finished_load = True
                self.ModuleSystem.RegisterUpdateSecond(self.OnUpdateSecond)

        self.DelayTickFunc(30, active)
