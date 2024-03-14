# -*- coding:utf-8 -*-


from const import *
from ..system.base import *
from ...client.entity import *
from ...common.system.event import ServerEvent, ClientEvent

if __name__ == '__main__':
    from server import PropertyModuleServer


class PropertyModuleClient(ModuleClientBase):
    """属性模块客户端"""
    __mVersion__ = 17
    __identifier__ = ModuleEnum.identifier

    def __init__(self):
        super(PropertyModuleClient, self).__init__()
        self.query_comp = self.comp_factory.CreateQueryVariable(self.local_id)
        self._syn_molang = set()
        self._player_name = {}
        self._is_jumping = False
        self._flag_holding_key_space = False

        self._inventory_update_recall = set()

        self.rpc = self.ModuleSystem.CreateRpcModule(self, ModuleEnum.identifier)

    def OnDestroy(self):
        del self._inventory_update_recall
        self.rpc.Discard()
        del self.rpc
        super(PropertyModuleClient, self).OnDestroy()

    def ConfigEvent(self):
        super(PropertyModuleClient, self).ConfigEvent()
        self.defaultEvent.update({
            # ClientEvent.OnScriptTickClient: self.OnScriptTickClient,
            ClientEvent.AddPlayerAOIClientEvent: self.AddPlayerAOIClientEvent,
            ClientEvent.ClientChestOpenEvent: self.ClientChestOpenEvent,
            ClientEvent.UiInitFinished: self.UiInitFinished,
            ClientEvent.OnKeyPressInGame: self.OnKeyPressInGame,
            ClientEvent.ClientJumpButtonPressDownEvent: self.ClientJumpButtonPressDownEvent,
        })
        self.clientEvent.update({
            ClientEvent.ClientModuleFinishedLoadEvent: self.ClientModuleFinishedLoadEvent,
        })
        self.serverEvent.update({
            ServerEvent.RequestSetMolangEvent: self.RequestSetMolangEvent,
            ServerEvent.RequestSynchronizeStorageEvent: self.RequestSynchronizeStorageEvent,
            ServerEvent.RequestSetRenderEvent: self.RequestSetRenderEvent,
            ModuleEvent.RequestPlayerMolangEvent: self.RequestPlayerMolangEvent,
            ModuleEvent.RequestDisplayRegisterMolangEvent: self.RequestDisplayRegisterMolangEvent,
            ModuleEvent.ModResponsePlayerNameEvent: self.ModResponsePlayerNameEvent,
        })

    # -----------------------------------------------------------------------------------

    def server(self):
        # type: () -> PropertyModuleServer
        return self.rpc

    # -----------------------------------------------------------------------------------

    def RegisterMolang(self, config):
        # type: (list) -> None
        """
        注册molang\n
        - 该值将用于同步
        """
        for molang in config:
            if molang not in self._syn_molang:
                self.query_comp.Register(molang, 0.0)
                self._syn_molang.add(molang)

    def RegisterInventoryUpdateRecall(self, recall):
        """
        注册背包缓存更新回调\n
        - 用于gui界面更新渲染原版背包
        - 默认传入此次的同步缓存数据 - 只读操作
        """
        self._inventory_update_recall.add(recall)

    def UnRegisterInventoryUpdateRecall(self, recall):
        """反注册背包缓存更新回调"""
        self._inventory_update_recall.discard(recall)

    def GetAllRegisterMolang(self, entity_id):
        # type: (str) -> dict
        """查询注册的molang"""
        storage = {}
        query_comp = self.comp_factory.CreateQueryVariable(entity_id)
        for key in self._syn_molang:
            storage[key] = query_comp.Get(key)
        return storage

    # -----------------------------------------------------------------------------------

    def GetPlayerName(self, playerId):
        # type: (str) -> str
        name = self._player_name.get(playerId)
        if not name:
            self.NotifyToServer(ModuleEvent.ModRequestGetPlayerNameEvent, {
                "playerId": self.local_id,
                "targetId": playerId
            })
            return RawEntity.GetChName(playerId)
        return name

    # -----------------------------------------------------------------------------------

    def UpdateEffectData(self, effect, level, duration, operate):
        # type: (str, int, int, str) -> None
        """更新原版效果缓存"""
        storage = self.local_player.GetEffect()
        if operate == "update":
            storage[effect] = (level, duration)
        elif operate == "remove":
            storage.pop(effect, None)

    def UpdateInventoryData(self, data):
        # type: (dict) -> None
        """更新原版背包缓存"""
        setattr(self.local_player, "_inventory", data)
        if self._inventory_update_recall:
            for recall in list(self._inventory_update_recall):
                if not callable(recall):
                    self._inventory_update_recall.discard(recall)
                    continue
                recall(data)

    # -----------------------------------------------------------------------------------

    def OnContinueJump(self):
        """连续跳检测"""
        self._is_jumping = False
        self.BroadcastEvent(ModuleEvent.OnPlayerJumpEvent, {})
        yield 2
        self._is_jumping = True

    # -----------------------------------------------------------------------------------

    def AddPlayerAOIClientEvent(self, args):
        playerId = args.get("playerId")
        self.NotifyToServer(ModuleEvent.RequestTargetMolangEvent, {
            "requestId": self.local_id,
            "targetId": playerId
        })
        if not self._player_name.get(playerId):
            self.NotifyToServer(ModuleEvent.ModRequestGetPlayerNameEvent, {
                "playerId": self.local_id,
                "targetId": playerId
            })

    def ClientModuleFinishedLoadEvent(self, _):
        pack = {"molang": []}
        self.BroadcastEvent(ModuleEvent.ModuleRequestLoadMolangConfigEvent, pack)
        config = pack.get("molang", [])
        if not isinstance(config, list):
            print "[error]", "invalid data:", config
            return
        self.RegisterMolang(list(set(config)))

    def ClientChestOpenEvent(self, args):
        if args["playerId"] != self.local_id:
            return
        self.NotifyToServer(ClientEvent.OnPlayerOpenChestEvent, {
            "playerId": self.local_id,
            "dim": self.GetDimension(),
            "pos": (args["x"], args["y"], args["z"])
        })

    def UiInitFinished(self, args):
        self.NotifyToServer(ClientEvent.UiInitFinished, {"playerId": self.local_id})

    # -----------------------------------------------------------------------------------

    def RequestPlayerMolangEvent(self, args):
        # type: (dict) -> None
        args["config"] = tuple({"molang": molang, "value": self.query_comp.Get(molang)} for molang in self._syn_molang)
        self.NotifyToServer(ModuleEvent.ResponsePlayerMolangEvent, args)

    def ModResponsePlayerNameEvent(self, args):
        entityId = args["entityId"]
        self._player_name[entityId] = args["name"]

    # -----------------------------------------------------------------------------------

    def RequestSynchronizeStorageEvent(self, args):
        # type: (dict) -> None
        self.local_player.SetStorage(args["key"], args["data"])

    def RequestSetMolangEvent(self, args):
        # type: (dict) -> None
        """
        请求设置molang事件\n
        - playerId: str
        - config: [dict]
            - molang: str
            - value: int
            - delay: float
        """
        playerId = args.get("playerId")
        config = args.get("config", [])
        queryComp = self.comp_factory.CreateQueryVariable(playerId)

        for data in config:
            assert isinstance(data, dict)
            molang, value = data["molang"], data["value"]
            delay = data.get("delay")
            if delay:
                self.game_comp.AddTimer(delay, queryComp.Set, molang, value)
                continue
            queryComp.Set(molang, value)

    def RequestSetRenderEvent(self, args):
        # type: (dict) -> None
        """
        请求渲染事件\n
        - playerId: str
        - geometry: str
        - texture: str
        """
        playerId = args.get("playerId")
        render = self.comp_factory.CreateActorRender(playerId)
        # -----------------------------------------------------------------------------------
        geometry = args.get("geometry")
        if geometry:
            render.AddPlayerGeometry(*geometry)
        texture = args.get("texture")
        if texture:
            render.AddPlayerTexture(*texture)
        render.RebuildPlayerRender()

    # -----------------------------------------------------------------------------------

    def OnScriptTickClient(self):
        # 连续跳检测
        if self._is_jumping:
            if self.local_player.IsOnGround():
                if self._flag_holding_key_space:
                    self.StartCoroutine(self.OnContinueJump)
                else:
                    self._is_jumping = False

    def ClientJumpButtonPressDownEvent(self, args):
        if args["continueJump"]:
            self._is_jumping = True
            self.BroadcastEvent(ModuleEvent.OnPlayerJumpEvent, {})

    def OnKeyPressInGame(self, args):
        if args["screenName"] == "hud_screen" and int(args["key"]) == KeyBoardType.KEY_SPACE:
            self._flag_holding_key_space = args["isDown"] == "1"

    def RequestDisplayRegisterMolangEvent(self, args):
        """请求显示注册molang"""
        print "[debug]", "================================="
        print "[debug]", "显示注册molang值：%s" % self.local_id
        for molang in self._syn_molang:
            print "[debug]", "%s: %s" % (molang, self.query_comp.Get(molang))
