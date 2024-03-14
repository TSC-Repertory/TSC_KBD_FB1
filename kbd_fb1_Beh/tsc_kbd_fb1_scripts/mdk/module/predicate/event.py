# -*- coding:utf-8 -*-


from parser import *
from ...server.entity import LivingEntity


class EventParserBase(BaseParser):
    """事件解析器"""
    __mVersion__ = 2

    def __init__(self, context):
        super(EventParserBase, self).__init__(context)
        self.host = self.context.get("host")  # type: str
        self.other = self.context.get("other")  # type: dict
        if not isinstance(self.other, dict):
            self.other = {}
        self.gameTimer = self.game_comp.AddTimer
        # -----------------------------------------------------------------------------------
        self._funcParser = FunctionParser(self.context)
        self._funcParser.SetOwner(self)
        self._conditionParser = ConditionParser(self.context)
        self._conditionParser.SetOwner(self)
        self._typeParser = TypeParser(self.context)
        self._typeParser.SetOwner(self)
        self._baseParser = BaseOnParser(self.context)
        self._baseParser.SetOwner(self)

    def Parse(self, target):
        # type: (dict) -> None
        """解析事件"""
        if not isinstance(target, dict):
            return
        events = target.get("events")  # type: list
        if not events:
            return
        for event in copy.deepcopy(events):
            assert isinstance(event, dict)
            eventKey = event.get("event")
            if not hasattr(self, eventKey):
                print "[error]", "无效事件：", eventKey
                continue
            if not self._conditionParser.Parse(event):
                continue
            getattr(self, eventKey)(event)


class EventParserPreset(EventParserBase):
    """预设事件解析器"""
    __mVersion__ = 1

    @staticmethod
    def _LoadPack(config):
        # type: (any) -> dict
        """发布事件"""
        delay = config.pop("delay", 0) if isinstance(config, dict) else 0
        dataPack = {
            "cancel": False,
            "config": config,
            "delay": delay
        }
        system = MDKConfig.GetModuleServer()
        system.BroadcastEvent(ServerEvent.PlayerEatFoodServerEvent, dataPack)
        return dataPack

    def add_item(self, pack):
        # type: (dict) -> None
        """
        解析添加物品\n
        - items: list<dict>
        """
        dataPack = []
        items = pack.get("items")  # type: list
        if not items:
            return
        for itemConfig in items:
            assert isinstance(itemConfig, dict)
            itemList = [itemConfig]
            if itemConfig.get("type"):
                if not self._conditionParser.Parse(itemConfig):
                    continue
                # todo: 暂时不支持无限解析TypeParser
                itemList = self._typeParser.Parse(itemConfig)
            for item in itemList:
                item["engine_type"] = "minecraft:item"
                if not item.get("count"):
                    item["count"] = 1  # 默认数量
                if not self._conditionParser.Parse(item):
                    continue
                self._funcParser.Parse(item)
                if not item.get("count") >= 1:
                    continue
                # 数据出口格式修正
                itemDict = {
                    "newItemName": item.get("name"),
                    "count": max(1, min(64, item.get("count"))),
                    "showInHand": item.get("show_in_hand", True),
                    "customTips": item.get("lore", "")
                    # 附魔
                    # 附加值
                }
                # 内容修正
                if "customName" in item:
                    item_comp = self.comp_factory.CreateItem(serverApi.GetLevelId())
                    item_comp.SetCustomName(itemDict, item["customName"])
                # 额外数据
                if "extraId" in item:
                    ServerItem.SetExtraId(itemDict, item["extraId"])
                dataPack.append(itemDict)
        dataPack = self._LoadPack(dataPack)
        if dataPack.get("cancel"):
            return
        entity = LivingEntity(self.host)
        for item in dataPack.get("config", []):
            assert isinstance(item, dict)
            entity.SpawnItem(item, **self.other)

    def cast_effect(self, pack):
        # type: (dict) -> None
        """
        解析添加药水效果\n
        - target: str
        - effects: list
        """
        effects = pack.get("effects")  # type: list
        target = pack.get("target", "self")
        victimId = self.host if target == "self" else self.other.get("id")
        if not victimId:
            print "[warn]", "Invalid victimId: %s" % victimId
            return
        outcome = []
        for effect in effects:
            assert isinstance(effect, dict)
            for key, value in effect.items():
                if isinstance(value, dict):
                    # 区间解析数值，可变键[duration, amplifier]，数据类型：int
                    effect[key] = int(round(RangeParser.Parse(value)))
            outcome.append(effect)
        dataPack = {"target": victimId, "effects": outcome}
        dataPack = self._LoadPack(dataPack)
        if dataPack.get("cancel"):
            return
        config = dataPack.get("config")  # type: dict
        victimId = config.get("target")  # type: str
        effects = config.get("effects")  # type: list
        effectComp = self.comp_factory.CreateEffect(victimId)
        for effect in effects:
            assert isinstance(effect, dict)
            effectComp.AddEffectToEntity(
                effect.get("effect"),
                effect.get("duration", 1),
                effect.get("amplifier", 0),
                effect.get("particle", True)
            )

    def cast_damage(self, pack):
        # type: (dict) -> None
        """
        解析伤害实体\n
        - attacker修正[未完善]
        - target: str
        - value: any
        """
        context = {"host": self.host, "other": self.other.get("id")}
        damage = pack.pop("damage", 1)
        if isinstance(damage, dict):
            # todo: 暂时只支持RangeParser
            damage = int(RangeParser.Parse(damage))
            # damage = self._baseParser.Parse(damage)
        target = pack.get("target", "self")
        victimId = context.get("host") if target == "self" else context.get("other")
        if not victimId:
            print "[warn]", "Invalid victimId: %s" % victimId
            return
        pack.update({"victimId": victimId, "damage": damage})
        dataPack = self._LoadPack(pack)
        if dataPack.get("cancel"):
            return
        config = dataPack.get("config")  # type: dict
        victimId = config.get("victimId")  # type: str

        def active():
            hurtComp = self.comp_factory.CreateGame(victimId)
            reset = False
            if config.get("force"):
                hurtComp.SetHurtCD(0)
                reset = True
            self.comp_factory.CreateHurt(victimId).Hurt(
                config.get("damage"),
                config.get("cause", minecraftEnum.ActorDamageCause.Override),
                config.get("attacker"),
                knocked=config.get("knock", True))
            if reset:
                hurtComp.SetHurtCD(10)

        delay = dataPack.get("delay")
        active() if not delay else self.gameTimer(delay, active)

    def trigger_event(self, pack):
        # type: (dict) -> None
        """
        解析脚本事件触发\n
        - 需要添加条件控制[未完善]
        - server: list
        - client: list
        """
        pack["entityId"] = self.GetContextId()
        dataPack = self._LoadPack(pack)
        config = dataPack.get("config")  # type: dict
        entityId = config.get("entityId")  # type: str
        system = MDKConfig.GetModuleServer()

        for event in config.get("server", []):
            assert isinstance(event, dict)
            eventName = event.get("name")
            params = event.get("params", {})
            params.update({"entityId": entityId})
            # Todo: 保留字修正
            system.BroadcastEvent(eventName, params)
        # -----------------------------------------------------------------------------------
        for event in config.get("client", []):
            assert isinstance(event, dict)
            eventName = event.get("name")
            params = event.get("params", {})
            params.update({"entityId": entityId})
            # Todo: 保留字修正
            system.BroadcastToAllClient(eventName, params)

    def send_message(self, pack):
        # type: (dict) -> None
        """解析信息发送"""
        target = pack.get("target", "self")
        entityId = self.host if target == "self" else self.other.get("id")
        pack.update({"entityId": entityId})
        dataPack = self._LoadPack(pack)
        if dataPack.get("cancel"):
            return
        config = dataPack.get("config")  # type: dict
        entityId = config.get("entityId")
        context = config.get("context")
        if config.get("popup"):
            self.game_comp.SetOneTipMessage(entityId, str(context))
        else:
            self.comp_factory.CreateMsg(serverApi.GetLevelId()).NotifyOneMessage(entityId, str(context))

    def run_command(self, pack):
        # type: (dict) -> None
        """解析指令"""
        if not pack.get("commands"):
            return
        dataPack = self._LoadPack(pack)
        if dataPack.get("cancel"):
            return
        config = dataPack.get("config")  # type: dict
        command_comp = self.comp_factory.CreateCommand(serverApi.GetLevelId())
        for command in config.get("commands", []):
            if isinstance(command, str):
                command_comp.SetCommand(command, self.host)
            elif isinstance(command, tuple) and len(command) == 2:
                _command, delay = command
                self.gameTimer(delay, command_comp.SetCommand, _command, self.host)

    def spawn_entity(self, pack):
        # type: (dict) -> None
        """解析召唤实体"""
        system = MDKConfig.GetModuleServer()
        pos = self.other.get("pos", RawEntity.GetPos(self.host))
        dim = self.other.get("dim", RawEntity.GetDim(self.host))
        for config in pack.get("entities", []):
            assert isinstance(config, dict)
            engineType = config.get("engine_type")
            entityId = system.CreateEngineEntityByTypeStr(engineType, pos, (0, 0), dim)
            config["target"] = entityId
            self._funcParser.Parse(config)
