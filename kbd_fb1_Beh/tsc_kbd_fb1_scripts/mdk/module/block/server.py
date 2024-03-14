# -*- coding:utf-8 -*-


from const import *
from parts.server.base import LogicBlockServerBase
from ..system.base import *
from ...interface.data.base import StoragePreset


class BlockModuleServer(ModuleServerBase, StoragePreset):
    """方块模块服务端"""
    __mVersion__ = 5
    __identifier__ = ModuleEnum.identifier
    _data_config = {
        "storage_key": MDKConfig.ModuleNamespace + "ModuleBlockStorage",  # 数据键
        "syn_data_key": ""  # 同步数据键 - 客户端缓存
    }

    def __init__(self):
        ModuleServerBase.__init__(self)
        StoragePreset.__init__(self)
        level_id = serverApi.GetLevelId()
        self.block_info_comp = self.comp_factory.CreateBlockInfo(level_id)
        self.block_data_comp = self.comp_factory.CreateBlockEntityData(level_id)
        self._request_data = False

        self._block_class_map = {}
        self._block_storage = {}

        self.block_destroy_recall = {}

    def OnDestroy(self):
        for block_ins in self._block_storage.values():
            block_ins.OnDestroy()
        del self._block_storage
        del self._block_class_map
        self.ModuleSystem.UnRegisterUpdateSecond(self.OnUpdateSecond)
        super(BlockModuleServer, self).OnDestroy()

    def ConfigEvent(self):
        super(BlockModuleServer, self).ConfigEvent()
        self.defaultEvent.update({
            ServerEvent.OnScriptTickServer: self.OnScriptTickServer,
            ServerEvent.ServerEntityTryPlaceBlockEvent: self.ServerEntityTryPlaceBlockEvent,
            ServerEvent.ServerPlayerTryDestroyBlockEvent: self.ServerPlayerTryDestroyBlockEvent,
            ServerEvent.PlayerIntendLeaveServerEvent: self.PlayerIntendLeaveServerEvent,
            ServerEvent.ClientLoadAddonsFinishServerEvent: self.ClientLoadAddonsFinishServerEvent,
        })
        self.clientEvent.update({
            UIEvent.OnUIOpenBlockScreenEvent: self.OnUIOpenBlockScreenEvent,
            UIEvent.OnUIExitBlockScreenEvent: self.OnUIExitBlockScreenEvent,
        })
        self.serverEvent.update({
            ServerEvent.ServerModuleFinishedLoadEvent: self.ServerModuleFinishedLoadEvent,
        })

    # -----------------------------------------------------------------------------------

    def RequestBlockClass(self):
        """请求方块类"""
        def active():
            if not self._block_class_map:
                print "[warn]", "empty block class map! destroying block module server."
                self.ModuleSystem.DelModule(ModuleEnum.identifier)
                return
            self.LoadData()
        self.DelayTickFunc(30, active)

    def RegisterBlockClass(self, block_name, block_cls):
        # type: (str, LogicBlockServerBase) -> None
        """注册方块类"""
        self._block_class_map[block_name] = block_cls

    def RegisterBlockDestroyRecall(self, block_name, block_id):
        # type: (str, tuple) -> None
        """
        注册方块破坏回调\n
        - 用于解决不常加载的方块数据清除问题
        - 例如方块数据含物品，摧毁后变成掉落物
        """
        if block_name not in self._block_class_map:
            return
        if block_name not in self.block_destroy_recall:
            self.block_destroy_recall[block_name] = []
        storage = self.block_destroy_recall[block_name]  # type: list
        storage.append(block_id)
        self.block_destroy_recall[block_name] = list(set(storage))
        self.flag_syn_data = True

    def UnRegisterBlockDestroyRecall(self, block_name, block_id):
        # type: (str, tuple) -> None
        """反注册方块破坏回调"""
        if block_name not in self.block_destroy_recall:
            return
        storage = self.block_destroy_recall[block_name]
        storage = set(storage)
        storage.discard(block_id)
        if not storage:
            self.block_destroy_recall.pop(block_name, None)
        else:
            self.block_destroy_recall[block_name] = list(storage)
        self.flag_syn_data = True

    # -----------------------------------------------------------------------------------

    def OnFinishedLoadData(self):
        self.ModuleSystem.RegisterUpdateSecond(self.OnUpdateSecond)

    # -----------------------------------------------------------------------------------

    def OnUpdateSecond(self):
        """服务端秒更新"""
        for block_ins in self._block_storage.values():
            block_ins.OnUpdateSecond()
        # 保存回调数据
        if self.flag_syn_data:
            self.flag_syn_data = False
            self.PackData()
            self.SaveData()

    def _CheckBlockDestroyRecall(self, block_name, block_id):
        # type: (str, tuple) -> None
        """检测方块摧毁回调"""
        if block_name not in self.block_destroy_recall:
            return
        storage = self.block_destroy_recall[block_name]
        if block_id not in storage:
            return
        storage = set(storage)
        storage.discard(block_id)
        self.block_destroy_recall[block_name] = list(storage)
        self.flag_syn_data = True
        block_ins = self.AddLogicBlock(block_id)
        block_ins.OnBlockDestroy()
        self.DelLogicBlock(block_id)

    # -----------------------------------------------------------------------------------

    """数据操作相关"""

    def ConfigRegisterData(self):
        self.RegisterData("block_destroy_recall", {})

    def HasLogicBlock(self, block_id):
        # type: (tuple) -> bool
        """是否存在逻辑方块"""
        return block_id in self._block_storage

    def GetLogicBlock(self, block_id):
        # type: (tuple) -> LogicBlockServerBase
        """获得逻辑方块实例"""
        return self._block_storage.get(block_id)

    def AddLogicBlock(self, block_id):
        # type: (tuple) -> LogicBlockServerBase
        """添加逻辑方块"""
        block_name = block_id[0]
        block_ins = self._block_class_map[block_name](*block_id)  # type: LogicBlockServerBase
        block_ins.LoadData()
        self._block_storage[block_id] = block_ins
        return block_ins

    def DelLogicBlock(self, block_id):
        # type: (tuple) -> None
        """删除逻辑方块"""
        block_ins = self._block_storage.pop(block_id, None)  # type: LogicBlockServerBase
        if block_ins:
            block_ins.OnDestroy()

    def GetData(self, key):
        return self.GetLevelStorage(key)

    def SetData(self, key, value):
        self.SetLevelStorage(key, value)

    # -----------------------------------------------------------------------------------

    def ServerModuleFinishedLoadEvent(self, args):
        if not self._request_data:
            self._request_data = True
            self.RequestBlockClass()

    def OnUIOpenBlockScreenEvent(self, args):
        # type: (dict) -> bool
        """
        UI打开方块界面事件\n
        playerId: str
        name: str
        dim: int
        pos: (int, int, int)
        """
        player_id = args["playerId"]
        name = args["name"]
        dim = args["dim"]
        pos = args["pos"]
        if self.block_info_comp.GetBlockNew(pos, dim)["name"] != name:
            return False
        block_id = (name, dim, pos)
        block_ins = self.GetLogicBlock(block_id)
        if block_ins:
            block_ins.AddPlayer(player_id)
            return True
        elif name not in self._block_class_map:
            return False
        block_ins = self.AddLogicBlock(block_id)
        block_ins.AddPlayer(player_id)
        return True

    def OnUIExitBlockScreenEvent(self, args):
        # type: (dict) -> None
        """客户端退出方块界面事件"""
        player_id = args["playerId"]
        block_id = args["blockId"]
        name, dim, pos = block_id
        if self.block_info_comp.GetBlockNew(pos, dim)["name"] != name:
            return
        block_ins = self.GetLogicBlock(block_id)
        if not block_ins:
            print "[warn]", "empty logic instance: %s" % name
            return
        block_ins.DelPlayer(player_id)

    def PlayerIntendLeaveServerEvent(self, args):
        playerId = args["playerId"]
        # 处理中途退出的情况
        for block_ins in self._block_storage.values():
            block_ins.DelPlayer(playerId)

    def ServerPlayerTryDestroyBlockEvent(self, args):
        name = args["fullName"]
        if name not in self._block_class_map:
            return

        dim = args["dimensionId"]
        pos = (args["x"], args["y"], args["z"])
        block_id = (name, dim, pos)

        block_ins = self.GetLogicBlock(block_id)
        if not block_ins:
            self._CheckBlockDestroyRecall(name, block_id)
            return
        # 触发逻辑方块销毁事件
        block_ins.OnBlockDestroy()
