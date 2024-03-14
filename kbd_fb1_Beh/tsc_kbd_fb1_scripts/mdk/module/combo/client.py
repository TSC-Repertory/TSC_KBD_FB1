# -*- coding:utf-8 -*-


from const import *
from ..system.base import *
from ...common.system.event import ClientEvent


# 下次使用需要修正成配置加载
class ComboModuleClient(ModuleClientBase):
    """连招模块客户端"""
    __identifier__ = ModuleEnum.identifier
    __mVersion__ = 6

    def __init__(self):
        super(ComboModuleClient, self).__init__()
        self.query_comp = self.comp_factory.CreateQueryVariable(self.local_id)
        self._config = {}
        self._task = {}

        # 动画Tick 正数动画时间 负数冷却时间
        self._anim_tick = 0
        self._anim_storage = {}

        self._is_combo = False
        self._task_flow = []
        self._pre_config = {}

        self.BroadcastEvent(ModuleEvent.OnFinishedInitComboModuleEvent, {})

    def ConfigEvent(self):
        super(ComboModuleClient, self).ConfigEvent()
        self.defaultEvent.update({
            ClientEvent.OnScriptTickClient: self.OnScriptTickClient,
        })
        self.clientEvent.update({
            ClientEvent.ClientModuleFinishedLoadEvent: self.ClientModuleFinishedLoadEvent,
            ModuleEvent.ClientActiveComboEvent: self.ClientActiveComboEvent,
        })
        self.serverEvent.update({
            ModuleEvent.ServerSynchronizeComboEvent: self.ServerSynchronizeComboEvent,
        })

    # -----------------------------------------------------------------------------------

    def RegisterConfig(self, config):
        # type: (dict) -> None
        """注册连招配置"""
        self._config.update(config)
        for key, _config in config.items():
            # print "[info]", "register combo:", key
            assert isinstance(_config, dict)
            molang = _config.get("molang")
            self.query_comp.Register(molang, 0.0)

    # -----------------------------------------------------------------------------------

    def OnScriptTickClient(self):
        """客户端Tick"""
        if self._anim_tick > 0:
            self._anim_tick -= 1
            if self._anim_tick == 0:
                self._OnAnimTickFinishedEvent()
        elif self._anim_tick < 0:
            self._anim_tick += 1

    def ClientModuleFinishedLoadEvent(self, _):
        pack = {}
        self.BroadcastEvent(ModuleEvent.ModuleRequestLoadComboConfigEvent, pack)
        self.RegisterConfig(pack)

    # -----------------------------------------------------------------------------------

    def _OnAnimTickFinishedEvent(self):
        """动画Tick完成事件"""
        if self._task_flow and self._is_combo:
            self._is_combo = False
            # 继续下一个动画任务
            config = self._task_flow.pop(0)  # type: dict
            self._anim_tick = config.get("duration")
            if isinstance(self._anim_tick, float):
                self._anim_tick = int(self._anim_tick * 30)
            # 服务端数据同步
            self.NotifyToServer(ModuleEvent.OnClientFinishedComboEvent, {
                "playerId": self.local_id,
                "molang": self._pre_config.get("molang"),
                "value": config.get("value"),
                "duration": self._anim_tick,
                "reset": config.get("reset")
            })
        else:
            # 设置冷却时间
            self._anim_tick = -1 * self._pre_config.get("reset", 10)
            self._pre_config = {}

    # -----------------------------------------------------------------------------------

    def ServerSynchronizeComboEvent(self, args):
        # type: (dict) -> None
        """
        服务端动画同步事件\n
        - playerId: str
        - molang: str
        - value: float
        - duration: float
        - reset: dict
            - molang: str
            - value: float
            - duration: float
            - reset: dict
        """
        playerId = args.get("playerId")
        molang = args.get("molang")
        value = args.get("value")
        duration = args.get("duration")

        lastGen = self._anim_storage.pop(playerId, None)
        if lastGen:
            self.StopCoroutine(lastGen)

        queryComp = self.comp_factory.CreateQueryVariable(playerId)
        queryComp.Set(molang, value)

        def active():
            # 动画时长
            yield duration
            reset = args.get("reset")  # type: dict
            while reset:
                _value = reset.get("value", 0)
                _duration = reset.get("duration", 0)
                queryComp.Set(molang, _value)
                yield duration
                if not reset:
                    break
                reset = reset.pop("reset", None)
            self._anim_storage.pop(playerId, None)

        self._anim_storage[playerId] = self.StartCoroutine(active)

    def ClientActiveComboEvent(self, args):
        # type: (dict) -> None
        """
        激活连招事件\n
        - playerId: str
        - moduleKey: str 使用的配置键
        - cancel: bool 是否取消
        """
        moduleKey = args.get("moduleKey")
        if self._anim_tick < 0:
            args["cancel"] = True
            # print "[error]", "冷却时间：%s" % self._anim_tick
        elif self._anim_tick > 0:
            config = self._config.get(moduleKey)
            if config != self._pre_config:
                # print "[warn]", "动画配置不一致"
                return
            if not self._task_flow:
                # print "[warn]", "本次动画已是最后一段"
                return
            config = self._task_flow[0]  # type: dict
            # 未达到响应时间
            if self._anim_tick > config.get("resetTick", 30):
                args["cancel"] = True
                # print "[warn]", "未达到响应时间"
                return
            self._is_combo = True
        else:
            self._pre_config = self._config.get(moduleKey)
            if not self._pre_config:
                print "[error]", "尚未配置连招动画:", moduleKey
                return
            self._is_combo = True
            self._task_flow = copy.deepcopy(self._pre_config.get("config"))  # type: list
            self._OnAnimTickFinishedEvent()
