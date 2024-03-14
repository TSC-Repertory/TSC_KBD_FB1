# -*- coding:utf-8 -*-


from const import *
from ..system.base import *
from ...client.entity import RawEntity
from ...common.system.event import ClientEvent
from ...common.utils.misc import *


class IndicatorModuleClient(ModuleClientBase):
    """伤害显示模块客户端"""
    __identifier__ = ModuleEnum.identifier
    __mVersion__ = 6

    def __init__(self):
        super(IndicatorModuleClient, self).__init__()
        self.text_comp = self.comp_factory.CreateTextBoard(self.local_id)

        self._entity_text_map = {}
        self._text_tick = {}

        # 隐藏血条
        self._hide_health_bar = {GameEntity.detector, GameEntity.projectile}

    def ConfigEvent(self):
        super(IndicatorModuleClient, self).ConfigEvent()
        self.defaultEvent.update({
            ClientEvent.OnScriptTickClient: self.OnScriptTickClient,
        })
        self.clientEvent.update({
            ClientEvent.ClientModuleFinishedLoadEvent: self.ClientModuleFinishedLoadEvent,
        })
        self.serverEvent.update({
            ModuleEvent.RequestDisplayDamageIndicatorEvent: self.RequestDisplayDamageIndicatorEvent
        })

    # -----------------------------------------------------------------------------------

    def OnScriptTickClient(self):
        for textId, config in self._text_tick.items():
            gen, color = config[:2]
            try:
                pos = gen.next()
            except StopIteration:
                self._text_tick.pop(textId, None)
                self.text_comp.RemoveTextBoard(textId)
                self._entity_text_map.pop(config[-1], None)
                del config
                continue
            # -----------------------------------------------------------------------------------
            """颜色渐变"""
            # rate = float(i) / 45
            # alpha = 1 - Misc.GetValueFromRate(rate, 0, 1.0)
            # newColor = tuple(list(color) + [1.0])
            self.text_comp.SetBoardTextColor(textId, color)
            # -----------------------------------------------------------------------------------
            """位置渐变"""
            self.text_comp.SetBoardPos(textId, pos)

    def ClientModuleFinishedLoadEvent(self, _):
        pack = {"active": False}
        self.BroadcastEvent(ModuleEvent.ModuleRequestHideEngineTypeHpBarEvent, pack)
        if not pack.get("active"):
            return
        # 开启血条显示
        engine_type = set(pack.get("engine_type", []))
        self._hide_health_bar.update(set(engine_type))
        # -----------------------------------------------------------------------------------
        self.defaultEvent[ClientEvent.AddEntityClientEvent] = self.AddEntityClientEvent
        self.ListenDefaultEvent(ClientEvent.AddEntityClientEvent, self.AddEntityClientEvent)
        self.game_comp.ShowHealthBar(True)

    def AddEntityClientEvent(self, args):
        engine_type = args["engineTypeStr"]
        heal_comp = self.comp_factory.CreateHealth(args["id"])
        heal_comp.ShowHealth(engine_type not in self._hide_health_bar)

    def RequestDisplayDamageIndicatorEvent(self, args):
        # type: (dict) -> None
        """
        请求伤害显示\n
        - entityId: str
        - value: int
        - pos: tuple
        - cause: str
        - color: tuple
        - crit: bool
        """
        entityId = args["entityId"]
        pos = args["pos"]
        value = args["value"]
        color = args.get("color", (1.0, 1.0, 1.0))
        # -----------------------------------------------------------------------------------
        text_color = tuple(list(color) + [1.0])
        # -----------------------------------------------------------------------------------
        textId = self.text_comp.CreateTextBoardInWorld(str(value), text_color)
        self.text_comp.SetBoardDepthTest(textId, False)
        self.text_comp.SetBoardBackgroundColor(textId, (0, 0, 0, 0))
        self.text_comp.SetBoardScale(textId, (2, 2))
        scale = 0
        if self.game_comp.IsEntityAlive(entityId):
            max_health = RawEntity.GetMaxHealth(entityId)
            scale = Misc.GetClamp(15.0 * value / (max_health - value * 0.5 + 0.001), 1.5, 4.0)
        self.StartCoroutine(self.DisplayDamageVersion2(textId, pos, value, scale))

    # -----------------------------------------------------------------------------------

    @staticmethod
    def sigmoid(x, a=1.0, o=0.0, d=0.0, m=1.0):
        """
        - a: float amplifier
        - o: float offset
        - d: float delay
        - m: float multi
        """
        return o + 1.0 * a / (1 + math.exp((-x + d) * m))

    # -----------------------------------------------------------------------------------

    def DisplayDamageVersion1(self, args):
        entityId = args["entityId"]
        value = args["value"]
        pos = args["pos"]
        color = args["color"]

        text_color = tuple(list(color) + [1.0])

        text_id = self._entity_text_map.get(entityId)
        if not text_id:
            text_id = self.text_comp.CreateTextBoardInWorld(str(value), text_color, (1.0, 1.0, 1.0, 0.0))
            self.text_comp.SetBoardFaceCamera(text_id, True)
            self.text_comp.SetBoardDepthTest(text_id, False)
            self.text_comp.SetBoardPos(text_id, pos)
            self.text_comp.SetBoardScale(text_id, (2.5, 2.5))
            if entityId:
                self._entity_text_map[entityId] = text_id
        else:
            config = self._text_tick.get(text_id)
            value += config[-2]
            self.text_comp.SetText(text_id, str(value))
            try:
                height = config[0].next()[1]
            except StopIteration:
                height = pos[1]
            pos = (pos[0], height, pos[2])

        endPos = Misc.GetPosModify(pos, (0, 0.25, 0))
        gen = Algorithm.lerpTupleInTime(pos, endPos, 0.4)
        self._text_tick[text_id] = [gen, text_color, value, entityId]

    def DisplayDamageVersion2(self, text_id, pos, value, scale=0):
        yield 0
        for i in range(30):
            height = self.sigmoid(i, a=0.8, m=0.5)
            display_pos = Misc.GetPosModify(pos, (0, height, 0))
            self.text_comp.SetBoardPos(text_id, display_pos)
            if scale:
                display_scale = Misc.GetPosModify((height,) * 2, (scale,) * 2)
                self.text_comp.SetBoardScale(text_id, display_scale)
            yield 1
        self.text_comp.RemoveTextBoard(text_id)
