# -*- coding:utf-8 -*-


from const import *
from ..system.base import *
from ...common.system.event import ServerEvent


class IndicatorModuleServer(ModuleServerBase):
    """伤害显示模块服务端"""
    __identifier__ = ModuleEnum.identifier
    __mVersion__ = 5

    def __init__(self):
        super(IndicatorModuleServer, self).__init__()
        self._audience = set()

    def ConfigEvent(self):
        super(IndicatorModuleServer, self).ConfigEvent()
        self.serverEvent.update({
            ModuleEvent.RequestDisplayDamageIndicatorEvent: self.RequestDisplayDamageIndicatorEvent
        })
        self.defaultEvent.update({
            ServerEvent.PlayerIntendLeaveServerEvent: self.PlayerIntendLeaveServerEvent,
            ServerEvent.ClientLoadAddonsFinishServerEvent: self.ClientLoadAddonsFinishServerEvent,
            ServerEvent.ActuallyHurtServerEvent: self.ActuallyHurtServerEvent,
            ServerEvent.CommandEvent: self.CommandEvent,
        })

    def RegisterAudience(self, playerId):
        # type: (str) -> None
        """注册伤害显示玩家"""
        self._audience.add(playerId)

    def UnRegisterAudience(self, playerId):
        # type: (str) -> None
        """反注册玩家显示伤害"""
        self._audience.discard(playerId)

    # -----------------------------------------------------------------------------------

    def ClientLoadAddonsFinishServerEvent(self, args):
        self.RegisterAudience(args["playerId"])

    def PlayerIntendLeaveServerEvent(self, args):
        self.UnRegisterAudience(args["playerId"])

    def ActuallyHurtServerEvent(self, args):
        entityId = args["entityId"]
        damage = args["damage"]
        cause = args["cause"]
        if damage <= 0:
            return
        pos = self.comp_factory.CreatePos(entityId).GetFootPos()
        if not pos:
            return
        size = self.comp_factory.CreateCollisionBox(entityId).GetSize()
        # -----------------------------------------------------------------------------------
        self.RequestDisplayDamageIndicatorEvent({
            "entityId": entityId,
            "value": damage,
            "cause": cause,
            "pos": (pos[0], pos[1] + size[1] - 0.5, pos[2]),
        })

    def RequestDisplayDamageIndicatorEvent(self, args):
        # type: (dict) -> None
        """
        请求伤害显示\n
        - entityId: str
        - value: int
        - pos: tuple
        - cause: str
        """
        entity_id = args["entityId"]
        value = args["value"]
        if value == 0:
            return

        if entity_id:
            tag_comp = self.comp_factory.CreateTag(entity_id)
            tags = tag_comp.GetEntityTags()
            if "indicator.crit" in tags:
                tag_comp.RemoveEntityTag("indicator.crit")
                args["crit"] = True

        self.NotifyToMultiClients(self._audience, ModuleEvent.RequestDisplayDamageIndicatorEvent, args)

    # -----------------------------------------------------------------------------------

    """
    指令控制：
    - /indicator disable -> 关闭显示
    - /indicator enable -> 开启显示
    """

    def CommandEvent(self, args):
        entity_id = args["entityId"]
        command = args["command"]  # type: str
        if command.startswith("/indicator disable"):
            self._audience.discard(entity_id)
        elif command.startswith("/indicator enable"):
            self._audience.add(entity_id)
