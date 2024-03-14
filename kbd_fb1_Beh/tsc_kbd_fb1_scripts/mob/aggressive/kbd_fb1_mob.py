# -*- coding:utf-8 -*-


from ...mdk import *
from ...mdk.common.utils import *
from ...mdk.server.entity import RawEntity, ProjectileEntity, SkillEntity, Entity, AttrEntity, PlayerEntity
from ...mdk.server.item.inventory import ServerInventoryMgr
from ...mob.base import ModEntityBase
from mod.common.minecraftEnum import ActorDamageCause
import random


class ModEntityAlcatraz(ModEntityBase):
    """
    生物基类
    """

    def __init__(self, entityId):
        super(ModEntityAlcatraz, self).__init__(entityId)
        self.ResetSkillTrigger()
        self.trigger_map = {
            "event:active_delayed_attack": self.TriggerAttack,
            "event:active_attack": self.ActiveAttack,
            "event:active_attack2": self.ActiveAttack,
            "event:active_skill1": self.ActiveSkill1,
            "event:active_skill2": self.ActiveSkill2,
            "event:active_skill3": self.ActiveSkill3,
            "event:reset_skill": self.ResetSkill
        }
        self._cd_counter = {}
        self.time_tick = 0
        config = modConfig.Fog_Man_EntityAttrConfig.get(self.type_str)
        if config:
            self.attack_cd = config.get("attack_cd", 60)
            self.sk1_cd = config.get("skill1_cd", 30)
            self.sk2_cd = config.get("skill2_cd", 30)
            self.sk3_cd = config.get("skill3_cd", 30)

    def ConfigEvent(self):
        super(ModEntityAlcatraz, self).ConfigEvent()
        self.defaultEvent.update({
            ServerEvent.OnScriptTickServer: self.OnScriptTickServer
        })

    def OnTriggerEvent(self, event_name):
        super(ModEntityAlcatraz, self).OnTriggerEvent(event_name)
        trigger = self.trigger_map.get(event_name)
        if trigger:
            trigger()

    def TriggerAttack(self):
        """触发攻击逻辑"""

    def ActiveAttack(self):
        """触发攻击"""
        if self._cd_counter.get(GameAttr.Attack):
            print "[warn]", "attack正在冷却：", self._cd_counter.get(GameAttr.Attack)
            return
        self._cd_counter[GameAttr.Attack] = self.attack_cd

    def ActiveSkill1(self):
        """触发技能1"""
        if self._cd_counter.get(GameAttr.skill1):
            print "[warn]", "skill正在冷却：", self._cd_counter.get(GameAttr.skill1)
            return
        self._cd_counter[GameAttr.skill1] = self.sk1_cd

    def ActiveSkill2(self):
        """触发技能2"""
        if self._cd_counter.get(GameAttr.skill2):
            print "[warn]", "skill正在冷却：", self._cd_counter.get(GameAttr.skill2)
            return
        self._cd_counter[GameAttr.skill2] = self.sk2_cd

    def ActiveSkill3(self):
        """触发技能3"""
        if self._cd_counter.get(GameAttr.skill3):
            print "[warn]", "skill正在冷却：", self._cd_counter.get(GameAttr.skill3)
            return
        self._cd_counter[GameAttr.skill3] = self.sk2_cd

    def ResetSkill(self):
        """重置技能"""

    def IsSkillOnCd(self, skill_key):
        # type: (str) -> bool
        """技能是否在冷却"""
        return skill_key in self._cd_counter
        # -----------------------------------------------------------------------------------

    def ResetSkillTrigger(self):
        """重置技能触发"""
        if not self.IsAlive():
            return
        self.TriggerCustomEvent("event:reset_skill")

    def OnScriptTickServer(self):

        for skill_key, cd in self._cd_counter.items():
            cd -= 1
            if cd <= 0:
                self._cd_counter.pop(skill_key, None)
                continue
            self._cd_counter[skill_key] = cd
        self.time_tick += 1
        if self.time_tick >= 30:
            self.time_tick = 0
            self.SecondUpdate()

    def SecondUpdate(self):
        """秒更新"""
        if not self.IsAlive():
            return

    def OnDealDamage(self, args):
        cause = args["cause"]
        if cause == ActorDamageCause.EntityAttack:
            args["damage"] = 0
            args["knock"] = False
            args["ignite"] = False

    def PlayCustomMusic(self, name, stop=0, loop=False, entity=None):
        """播放音效"""
        if not self.IsAlive():
            return
        if not entity:
            entity = self.id
        self.BroadcastToAllClient(ServerEvent.RequestPlayMusicEvent, {
            "entityId": entity,
            "name": name,
            "stop": stop,
            "loop": loop
        })

    def StopCustomMusic(self, entityId):
        self.BroadcastToAllClient("StopMusic", {
            "entityId": entityId
        })

    def SetMoveFalse(self, playerId, value=0.8):
        """禁止玩家移动"""
        comp = self.comp_factory.CreatePlayer(playerId)
        comp.SetPlayerMovable(False)
        self.game_comp.AddTimer(value, comp.SetPlayerMovable, True)


class FogManEntity(ModEntityAlcatraz):
    """雾中人"""

    def __init__(self, entityId):
        super(FogManEntity, self).__init__(entityId)
        self.live_time = 0
        self.live_time2 = 0
        self.see_time = 0
        if modConfig.BeforeTime:
            self.TriggerCustomEvent("event:before_time")

    def OnDealDamage(self, args):
        pass

    def SecondUpdate(self):
        super(FogManEntity, self).SecondUpdate()
        target = self.GetAttackTarget()
        if target and not self.HasTag("can_attack"):
            player_list = self.GetMobInRadius(15, filters=GameFilter.Player)
            if target in player_list:
                RawEntity.Create(GameEntity.lightning_bolt, dim=self.dim, pos=self.foot_pos)
                self.TriggerCustomEvent("event:can_attack")
                self.AddTag("can_attack")
                if not modConfig.BeforeTime:
                    self.game_comp.AddTimer(3, self.PlayCustomMusic, "zdkj.chasedv2", loop=True)

        if self.HasTag("can_attack"):
            self.live_time += 1
            if self.live_time >= 30:
                RawEntity.Create(GameEntity.lightning_bolt, dim=self.dim, pos=self.foot_pos)
                self.Destroy(0.1)
        else:
            self.live_time2 += 1
            if self.live_time2 >= 120:
                self.Destroy(0.1)

