# -*- coding:utf-8 -*-


from const import *
from ..system.base import *
from ...server.entity import *

if __name__ == '__main__':
    from client import PropertyModuleClient


class PropertyModuleServer(ModuleServerBase):
    """属性模块服务端"""
    __mVersion__ = 10
    __identifier__ = ModuleEnum.identifier

    def __init__(self):
        super(PropertyModuleServer, self).__init__()
        self._on_tick = False
        self._syn_inv = {}
        self.rpc = self.ModuleSystem.CreateRpcModule(self, ModuleEnum.identifier)

    def OnDestroy(self):
        self.rpc.Discard()
        del self.rpc
        del self._syn_inv
        super(PropertyModuleServer, self).OnDestroy()

    def ConfigEvent(self):
        super(PropertyModuleServer, self).ConfigEvent()
        self.defaultEvent.update({
            ServerEvent.AddEffectServerEvent: self.UpdateEffectServerEvent,
            ServerEvent.RemoveEffectServerEvent: self.RemoveEffectServerEvent,
            ServerEvent.RefreshEffectServerEvent: self.UpdateEffectServerEvent,
            ServerEvent.InventoryItemChangedServerEvent: self.InventoryItemChangedServerEvent,
        })
        self.clientEvent.update({
            ModuleEvent.ModRequestGetPlayerNameEvent: self.ModRequestGetPlayerNameEvent,
            ModuleEvent.RequestTargetMolangEvent: self.RequestTargetMolangEvent,
            ModuleEvent.ResponsePlayerMolangEvent: self.ResponsePlayerMolangEvent,
        })

    # -----------------------------------------------------------------------------------

    def client(self, target=None):
        # type: (str) -> PropertyModuleClient
        return self.rpc(target)

    # -----------------------------------------------------------------------------------

    def UpdateEffectServerEvent(self, args):
        entity_id = args.get("entityId")
        if RawEntity.IsPlayer(entity_id):
            effect = args["effectName"]
            level = args["effectAmplifier"]
            duration = args["effectDuration"]
            self.client(entity_id).UpdateEffectData(effect, level, duration, "update")

    def RemoveEffectServerEvent(self, args):
        entity_id = args.get("entityId")
        if RawEntity.IsPlayer(entity_id):
            effect = args["effectName"]
            level = args["effectAmplifier"]
            duration = args["effectDuration"]
            self.client(entity_id).UpdateEffectData(effect, level, duration, "remove")

    # -----------------------------------------------------------------------------------

    def OnScriptTickServer(self):
        for playerId, tick in self._syn_inv.items():
            tick -= 1
            if tick < 0:
                self._syn_inv.pop(playerId, None)
                self.client(playerId).UpdateInventoryData(self.Inventory(playerId).GetAllItemsFormat())
                continue
            self._syn_inv[playerId] = tick
        if not self._syn_inv:
            self._on_tick = False
            self.UnListenDefaultEvent(ServerEvent.OnScriptTickServer, self.OnScriptTickServer)

    def InventoryItemChangedServerEvent(self, args):
        playerId = args.get("playerId")
        self._syn_inv[playerId] = 1
        if not self._on_tick:
            self.ListenDefaultEvent(ServerEvent.OnScriptTickServer, self.OnScriptTickServer)

    # -----------------------------------------------------------------------------------

    def RequestTargetMolangEvent(self, args):
        # type: (dict) -> None
        self.NotifyToClient(args["targetId"], ModuleEvent.RequestPlayerMolangEvent, args)

    def ResponsePlayerMolangEvent(self, args):
        # type: (dict) -> None
        args["playerId"] = args["targetId"]
        self.NotifyToClient(args["requestId"], ServerEvent.RequestSetMolangEvent, args)

    def ModRequestGetPlayerNameEvent(self, args):
        playerId = args["playerId"]
        targetId = args["targetId"]
        name = self.comp_factory.CreateName(targetId).GetName()
        self.NotifyToClient(playerId, ModuleEvent.ModResponsePlayerNameEvent, {"entityId": targetId, "name": name})
