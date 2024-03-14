# -*- coding:utf-8 -*-


from ....server.system.base import *


class ModuleDungeonInterface(object):
    """关卡类接口"""
    __mVersion__ = 1

    def OnPlayerRespawnFinished(self, player_id):
        # type: (str) -> None
        """玩家重生到该副本维度触发"""


class ModuleDungeonBase(ServerBaseSystem, ModuleDungeonInterface):
    """关卡基类"""
    __mVersion__ = 5

    def __init__(self, dim_id, *args, **kwargs):
        super(ModuleDungeonBase, self).__init__(MDKConfig.GetModuleServer(), *args, **kwargs)
        level_id = serverApi.GetLevelId()
        self.chunk_comp = self.comp_factory.CreateChunkSource(level_id)
        # 维度Id
        self._dim_id = dim_id
        # 玩家数据
        self.player_set = set()
        # 副本是否激活
        self._is_active = False

        # print "[suc]", "创建副本关卡：%s" % self.__class__.__name__

    def ConfigEvent(self):
        super(ModuleDungeonBase, self).ConfigEvent()
        self._is_active = True

    # -----------------------------------------------------------------------------------

    @property
    def id(self):
        # type: () -> int
        """维度Id作为本实例的标识"""
        return self._dim_id

    def GetDimId(self):
        # type: () -> int
        """获得维度Id"""
        return self._dim_id

    _dungeon_module = None

    @property
    def DungeonModule(self):
        # type: () -> MDKConfig.GetPresetModule().DungeonModuleServer
        if ModuleDungeonBase._dungeon_module:
            return ModuleDungeonBase._dungeon_module
        module = self.ModuleSystem.GetModule(MDKConfig.GetPresetModule().DungeonModuleServer.GetId())
        if not module:
            return None
        ModuleDungeonBase._dungeon_module = weakref.proxy(module)
        return ModuleDungeonBase._dungeon_module

    def DiscardDungeon(self):
        """删除副本实例"""
        self.DungeonModule.DelDungeonIns(id(self))

    def DiscardDungeonIfEmptyPlayer(self):
        """如果没有玩家在维度则关闭实例"""
        if not self.HasAnyPlayer():
            self.DiscardDungeon()

    # -----------------------------------------------------------------------------------

    def RegisterBanDestroy(self):
        """注册禁止破坏"""
        self.DungeonModule.RegisterBanDestroyDim(self.id)

    def UnRegisterBanDestroy(self):
        """反注册禁止破坏"""
        self.DungeonModule.UnRegisterBanDestroyDim(self.id)

    # -----------------------------------------------------------------------------------

    def OnUpdateSecond(self):
        """
        副本秒更新\n
        - 由管理调用
        """

    # -----------------------------------------------------------------------------------

    def IsActive(self):
        # type: () -> bool
        """副本是否在运行"""
        return self._is_active

    def Activate(self):
        """手动启动副本"""
        self._is_active = True
        self.BatchListenDefault(self.defaultEvent)

    def Deactivate(self):
        """手动关闭副本"""
        self._is_active = False
        self.BatchUnListenDefault(self.defaultEvent)

    # -----------------------------------------------------------------------------------

    """玩家相关"""

    def AddPlayer(self, player_id):
        # type: (str) -> None
        """
        添加玩家至副本实例\n
        - 需要切换维度完成事件后才触发
        """
        self.player_set.add(player_id)

    def DelPlayer(self, player_id):
        # type: (str) -> None
        """从副本实例删除玩家"""
        self.player_set.discard(player_id)

    def HasPlayer(self, player_id):
        # type: (str) -> bool
        """玩家是否存在"""
        return player_id in self.player_set

    def HasAnyPlayer(self):
        # type: () -> bool
        """判断维度是否有玩家"""
        return len(self.player_set) > 0

    def DelPlayerFog(self, player_id, fog):
        """重置玩家迷雾"""
        fog_str = fog.split(":")[-1]
        self.command_comp.SetCommand("/fog @s remove %s" % fog_str, player_id)

    def SetPlayerFog(self, player_id, fog):
        """设置玩家迷雾"""
        fog_str = fog.split(":")[-1]
        self.command_comp.SetCommand("/fog @s push %s %s" % (fog, fog_str), player_id)

    # -----------------------------------------------------------------------------------

    """场景相关"""

    def CheckBlock(self, block_pos, block_name):
        # type: (tuple, any) -> bool
        """判断位置方块"""
        if not isinstance(block_name, list):
            block_name = list(block_name)
        return self.block_comp.GetBlockNew(block_pos, self._dim_id).get("name") in block_name

    def SetBlock(self, block_pos, block_name, aux=0):
        # type: (tuple, str, int) -> bool
        """设置方块"""
        return self.block_comp.SetBlockNew(block_pos, {"name": block_name, "aux": aux}, 0, self._dim_id)

    def GetBlockTop(self, pos):
        # type: (tuple) -> tuple
        """获得该位置的最高方块位置"""
        return self.block_comp.GetTopBlockHeight((pos[0], pos[2]), self._dim_id)

    def SpawnEntity(self, engine_type, spawn_pos):
        # type: (str, tuple) -> str
        """生成实体"""
        return self.AddEntity(engine_type, spawn_pos, self._dim_id)


class ModuleDungeonGameBase(ModuleDungeonBase):
    """关卡副本基类"""
    __mVersion__ = 1


class ModuleDungeonLobbyBase(ModuleDungeonBase):
    """关卡大厅基类"""
    __mVersion__ = 1
