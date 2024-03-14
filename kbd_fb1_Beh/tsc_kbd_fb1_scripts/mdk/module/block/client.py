# -*- coding:utf-8 -*-


from const import *
from parts.client.base import LogicBlockClientBase
from ..system.base import *


class BlockModuleClient(ModuleClientBase):
    """
    方块模块客户端\n
    - 注册进模块的逻辑方块在右键时启用
    """
    __mVersion__ = 2
    __identifier__ = ModuleEnum.identifier

    def __init__(self):
        super(BlockModuleClient, self).__init__()
        level_id = clientApi.GetLevelId()
        self.block_info_comp = self.comp_factory.CreateBlockInfo(level_id)

        self._block_class_map = {}
        self._block_storage = {}
        self._block_cd = {}

    def OnDestroy(self):
        for timer in self._block_cd.values():
            self.game_comp.CancelTimer(timer)
        del self._block_cd
        del self._block_class_map
        for block_ins in self._block_storage.values():
            block_ins.OnDestroy()
        del self._block_storage
        super(BlockModuleClient, self).OnDestroy()

    def ConfigEvent(self):
        super(BlockModuleClient, self).ConfigEvent()
        self.defaultEvent.update({
            ClientEvent.ClientBlockUseEvent: self.ClientBlockUseEvent,
        })
        self.clientEvent.update({
            ClientEvent.ClientModuleFinishedLoadEvent: self.ClientModuleFinishedLoadEvent,
        })
        self.serverEvent.update({
            ModuleEvent.ModuleRequestShuntDownBlockEvent: self.ModuleRequestShuntDownBlockEvent,
            ModuleEvent.ModuleOnBlockAddPlayerEvent: self.ModuleOnBlockAddPlayerEvent,
        })

    # -----------------------------------------------------------------------------------

    def RegisterBlockClass(self, block_name, block_cls):
        # type: (str, LogicBlockClientBase) -> None
        """注册方块类"""
        self._block_class_map[block_name] = block_cls

    # -----------------------------------------------------------------------------------

    """方块数据相关"""

    def AddLogicBlock(self, block_id):
        # type: (tuple) -> LogicBlockClientBase
        """添加逻辑方块"""
        block_name = block_id[0]
        block_ins = self._block_class_map[block_name](*block_id)  # type: LogicBlockClientBase
        block_ins.LoadData()
        self._block_storage[block_id] = block_ins
        return block_ins

    def DelLogicBlock(self, block_id):
        # type: (tuple) -> None
        """删除逻辑方块"""
        block_ins = self._block_storage.pop(block_id, None)  # type: LogicBlockClientBase
        if block_ins:
            block_ins.OnDestroy()

    # -----------------------------------------------------------------------------------

    def ClientModuleFinishedLoadEvent(self, _):
        """请求方块类"""
        pack = {"add": self.RegisterBlockClass}
        self.BroadcastEvent(ModuleEvent.ModuleRequestBlockClassMapEvent, pack)
        if not self._block_class_map:
            print "[warn]", "empty block class map! destroying block module client."
            self.ModuleSystem.DelModule(ModuleEnum.identifier)

    def ModuleRequestShuntDownBlockEvent(self, args):
        # type: (dict) -> None
        """请求关闭逻辑方块"""
        block_id = args["blockId"]
        block_name = block_id[0]
        if block_name not in self._block_class_map:
            return
        block_ins = self._block_storage.get(block_id)  # type: LogicBlockClientBase
        if not block_ins:
            return
        block_ins.OnServerRequestShuntDown()
        self.DelLogicBlock(block_id)

    def ClientBlockUseEvent(self, args):
        player_id = args["player_id"]
        if player_id != self.local_id:
            return
        block_name = args["blockName"]
        if block_name in self._block_cd:
            return
        self._block_cd[block_name] = self.game_comp.AddTimer(0.1, lambda: self._block_cd.pop(block_name, None))

        block_cls = self._block_class_map.get(block_name)
        if not block_cls:
            return

        block_pos = (args["x"], args["y"], args["z"])
        block_id = (block_name, self.GetDimension(), block_pos)
        self.AddLogicBlock(block_id)

    def ModuleOnBlockAddPlayerEvent(self, args):
        # type: (dict) -> None
        block_id = args["id"]
        block_name = block_id[0]
        if block_name not in self._block_class_map:
            return
        block_ins = self._block_storage.get(block_id)  # type: LogicBlockClientBase
        if not block_ins:
            return
        block_ins.OnServerBlockAddPlayer(args["rpc"], args["data"])
