# -*- coding:utf-8 -*-


import re

from const import *
from ..system.base import *
from ...server.system.preset import *

if __name__ == '__main__':
    from client import DebugModuleClient
    from ui.root import DebugScreen


class DebugModuleServer(ModuleServerBase):
    """Debug模块服务端"""
    __mVersion__ = 12
    __identifier__ = ModuleEnum.identifier

    def __init__(self):
        super(DebugModuleServer, self).__init__()
        level_id = serverApi.GetLevelId()
        self.command_comp = self.comp_factory.CreateCommand(level_id)
        self.block_comp = self.comp_factory.CreateBlockInfo(level_id)
        self.biome_comp = self.comp_factory.CreateBiome(level_id)
        self.item_comp = self.comp_factory.CreateItem(level_id)
        self.time_comp = self.comp_factory.CreateTime(level_id)

        self.rpc = self.ModuleSystem.CreateRpcModule(self, "debug")
        self.rpc_ui = self.ModuleSystem.CreateRpcModule(self, "debug.ui")

    def ConfigEvent(self):
        super(DebugModuleServer, self).ConfigEvent()
        self.defaultEvent.update({
            ServerEvent.CommandEvent: self.CommandEvent
        })
        self.clientEvent.update({
            ModuleEvent.ModuleRequestUpdateFocusEntityEvent: self.ModuleRequestUpdateFocusEntityEvent,
            # ClientEvent.OnKeyPressInGame: self.OnKeyPressInGame
        })

    def OnDestroy(self):
        self.rpc.Discard()
        self.rpc_ui.Discard()
        del self.rpc
        del self.rpc_ui
        super(DebugModuleServer, self).OnDestroy()

    def client(self, target=None):
        # type: (str) -> DebugModuleClient
        return self.rpc(target)

    def ui(self, target=None):
        # type: (str) -> DebugScreen
        return self.rpc_ui(target)

    # -----------------------------------------------------------------------------------

    def CheckTargetAvailableStorageKey(self, target_id, storage_key):
        # type: (str, str) -> None
        """检测目标的数据键是否有效"""
        storages = LivingEntity(target_id).GetAllStorage()
        self.ui(target_id).OnResponseStorageKeyCheck(storage_key, storage_key in storages)

    def RequestTargetStorageKey(self, player_id, target_id):
        # type: (str, str) -> None
        """请求目标的全部数据键"""
        entity = LivingEntity(target_id)
        storage = entity.GetAllStorage()
        context = ["entity_id: %s" % target_id, "engine_type: %s\n" % entity.type_str]
        for index, key in enumerate(storage):
            context.append("<%s> %s" % (index + 1, key))
        self.ui(player_id).SetInputPanelTips("\n".join(context))

    def GetTargetStorage(self, target_id, storage_key):
        # type: (str, str) -> None
        """获得目标数据"""
        storage = LivingEntity(target_id).GetStorage(storage_key)
        self.ui(target_id).OnUpdateScrollText(storage_key, storage)

    def SetWorldTime(self, rate):
        # type: (float) -> None
        """设置时间"""
        self.time_comp.SetTime(int((rate * 24000 + 23000) % 24000))

    # -----------------------------------------------------------------------------------

    def ToggleGameMode(self, player_id):
        # type: (str) -> None
        """切换游戏模式"""
        gamemode = self.game_comp.GetPlayerGameType(player_id)
        self.comp_factory.CreatePlayer(player_id).SetPlayerGameType((gamemode + 1) % 2)

    def GetBiomeInfo(self, pos, dim):
        # type: (tuple, int) -> str
        """获得群系信息"""
        return self.biome_comp.GetBiomeName(pos, dim)

    def SetCommands(self, player_id, commands):
        # type: (str, list) -> None
        """执行指令"""
        for command in commands:
            self.command_comp.SetCommand(command, player_id)

    # -----------------------------------------------------------------------------------

    def QueryServerModuleInfo(self, player_id):
        """查询服务端模块信息"""
        module_info = {}
        for module_key in self.ModuleSystem.GetAllModule():
            module_ins = self.ModuleSystem.GetModule(module_key)  # type: ModuleServerBase
            module_info[module_key] = module_ins.GetVersion()
        self.ui(player_id).OnResponseModuleInfo(module_info)

    # -----------------------------------------------------------------------------------

    @classmethod
    def ModuleRequestUpdateFocusEntityEvent(cls, args):
        entityId = args["entityId"]
        control = args["control"]
        data = args["data"]

        entity = LivingEntity(entityId)
        if control == "ride_offset":
            offset = data["offset"]
            entity.SetRidePos(offset)
        elif control == "collision_size":
            size = data["size"]
            entity.SetCollisionBoxSize(size)

    def CommandEvent(self, args):
        entity_id = args["entityId"]
        command = args["command"]  # type: str

        if command == "/effect @s clear all":
            effect_comp = self.comp_factory.CreateEffect(entity_id)
            effect_list = effect_comp.GetAllEffects()
            if effect_list:
                for effect in effect_list:
                    effect_comp.RemoveEffectFromEntity(effect["effectName"])
            args["cancel"] = True
        elif command == "/debug molang":
            self.NotifyToClient(entity_id, ModuleEvent.RequestDisplayRegisterMolangEvent, {})
            args["cancel"] = True
        elif command.startswith("/debug group "):
            group_key = re.findall("/debug group (.*)", command)[0]
            if not self.AttrModule:
                print "[warn]", "attribute module do not exist!"
            else:
                print "[suc]", "group_key: %s" % group_key
                res = self.AttrModule.GetEntityIns(entity_id).GetGroup(group_key)
                for _key, _value in res.iteritems():
                    print "[warn]", _key, ":", _value
            args["cancel"] = True
        elif command.startswith("/set skin "):
            path = re.findall("/set skin (.*)", command)[0]
            self.client(entity_id).SetClientSkin(path)
            args["cancel"] = True
        elif command.startswith("/quest query active"):
            quest_entity = self.QuestModule.GetQuestEntity(entity_id)
            if quest_entity:
                for quest_id, quest_progress in quest_entity.GetQuestData().iteritems():
                    print "[suc]", "%s: %s" % (quest_id, quest_progress)
            args["cancel"] = True

    def OnKeyPressInGame(self, args):
        player_id, is_down, key = super(DebugModuleServer, self).OnKeyPressInGame(args)
        if not is_down:
            return
