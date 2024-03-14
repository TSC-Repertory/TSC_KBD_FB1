# -*- coding:utf-8 -*-


from ....server.system.base import *

"""
模块实体基类
- 构造后的生物类需要注册到 <MobModuleServer> 方可生效
- 目前采用集中管理触发回调，减少大量实体监听事件的压力
- 构造自定义模组玩家和生物的基类，可通过继承 <ModuleEntityMgr> 

- 目前版本并没有伤害类型过滤，需要手动处理
"""


class ModuleEntityMgr(ServerBaseSystem):
    """
    模块实体管理\n
    - 提供常用触发接口
    """
    __mVersion__ = 3

    def OnHitRecall(self, hit_list):
        # type: (list) -> None
        """碰撞回调"""

    # -----------------------------------------------------------------------------------

    """造成伤害"""

    def OnDealDamage(self, args):
        # type: (dict) -> None
        """
        实体造成伤害时触发\n
        - srcId: str 伤害源id
        - projectileId: str 投射物id
        - entityId: str 被伤害id
        - damage: int 伤害值，允许修改，设置为0则此次造成的伤害为0
        - absorption: int 伤害吸收生命值，详见AttrType枚举的ABSORPTION
        - cause: str 伤害来源，详见Minecraft枚举值文档的ActorDamageCause
        - knock: bool 是否击退被攻击者，允许修改，设置该值为False则不产生击退
        - ignite: bool 是否点燃被伤害者，允许修改，设置该值为True产生点燃效果，反之亦然
        """

    def OnActuallyDealDamage(self, args):
        # type: (dict) -> None
        """
        实体实际造成伤害\n
        实体实际受到伤害时触发，相比于DamageEvent，该伤害为经过护甲及buff计算后，实际的扣血量\n
        - srcId: str 伤害源id
        - projectileId: str 投射物id
        - entityId: str 被伤害id
        - damage: int 伤害值，允许修改，设置为0则此次造成的伤害为0
        - cause: str 伤害来源，详见Minecraft枚举值文档的ActorDamageCause
        """

    def OnKillEntity(self, victimId):
        # type: (str) -> None
        """
        实体杀死其他实体触发\n
        - victimId: str
        """

    """承受伤害"""

    def OnTookDamage(self, args):
        # type: (dict) -> None
        """
        实体受到伤害时触发\n
        - srcId: str 伤害源id
        - projectileId: str 投射物id
        - entityId: str 被伤害id
        - damage: int 伤害值，允许修改，设置为0则此次造成的伤害为0
        - absorption: int 伤害吸收生命值，详见AttrType枚举的ABSORPTION
        - cause: str 伤害来源，详见Minecraft枚举值文档的ActorDamageCause
        - knock: bool 是否击退被攻击者，允许修改，设置该值为False则不产生击退
        - ignite: bool 是否点燃被伤害者，允许修改，设置该值为True产生点燃效果，反之亦然
        """

    def OnActuallyTookDamage(self, args):
        # type: (dict) -> None
        """
        实体实际承受伤害\n
        实体实际受到伤害时触发，相比于DamageEvent，该伤害为经过护甲及buff计算后，实际的扣血量\n
        - srcId: str 伤害源id
        - projectileId: str 投射物id
        - entityId: str 被伤害id
        - damage: int 伤害值，允许修改，设置为0则此次造成的伤害为0
        - cause: str 伤害来源，详见Minecraft枚举值文档的ActorDamageCause
        """

    """交互相关"""

    def OnTriggerEvent(self, event_name):
        # type: (str) -> None
        """实体触发生物事件"""

    def OnInteractedByPlayer(self, player_id, item_dict):
        # type: (str, dict) -> None
        """
        玩家与有minecraft:interact组件的生物交互时触发该事件\n
        例如玩家手持空桶对牛挤奶、玩家手持打火石点燃苦力怕
        """

    """生命相关"""

    def OnFinalDelHealth(self, value):
        # type: (int) -> None
        """最终减少生命"""

    def OnFinalAddHealth(self, value):
        # type: (int) -> None
        """最终增加生命"""

    """死亡相关"""

    def OnWillDie(self, args):
        # type: (dict) -> None
        """
        实体将要死亡事件\n
        可用于死亡前无敌然后播放动画特效等\n
        ----\n        - srcId: str 伤害源id
        - projectileId: str 投射物id
        - entityId: str 被伤害id
        - damage: int 伤害值，允许修改，设置为0则此次造成的伤害为0
        - cause: str 伤害来源，详见Minecraft枚举值文档的ActorDamageCause
        """

    def OnDeath(self, killer):
        # type: (str) -> None
        """
        实体死亡事件\n
        - killer: str 击杀者Id
        """


class ModuleEntityPreset(ModuleEntityMgr, LivingEntity):
    """模块实体预设"""
    __mVersion__ = 2

    def __init__(self, entityId):
        ModuleEntityMgr.__init__(self, MDKConfig.GetModuleServer())
        LivingEntity.__init__(self, entityId)

    def OnDestroy(self):
        ModuleEntityMgr.OnDestroy(self)

    _mob_module = None

    @property
    def MobModule(self):
        # type: () -> MDKConfig.GetPresetModule().MobModuleServer
        if ModuleEntityPreset._mob_module:
            return ModuleEntityPreset._mob_module
        module = self.ModuleSystem.GetModule(MDKConfig.GetPresetModule().MobModuleServer.GetId())
        if not module:
            return None
        ModuleEntityPreset._mob_module = weakref.proxy(module)
        return ModuleEntityPreset._mob_module

    def RegisterHitRecall(self):
        """注册碰撞回调"""
        if not self.MobModule:
            return
        self.MobModule.RegisterHitDetection(self.id)

    def UnRegisterHitRecall(self):
        """反注册碰撞回调"""
        if not self.MobModule:
            return
        self.MobModule.UnRegisterHitDetection(self.id)
