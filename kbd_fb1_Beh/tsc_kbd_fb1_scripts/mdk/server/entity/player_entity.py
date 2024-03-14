# -*- coding:utf-8 -*-


import mod.server.extraServerApi as serverApi

from living_entity import LivingEntity
from ...common.utils.misc import Misc
from ...loader import MDKConfig


class PlayerEntity(LivingEntity):
    """玩家实例基类"""
    __mVersion__ = 10

    def __init__(self, playerId):
        super(PlayerEntity, self).__init__(playerId)
        self.player_comp = self.comp_factory.CreatePlayer(self.id)

    def SetPlayerNaturalRegen(self, active):
        # type: (bool) -> bool
        """
        设置是否开启玩家自然恢复\n
        - 当饥饿值大于等于健康临界值时会自动恢复血量
        - 开启饥饿值且开启自然恢复时有效.原版默认开启
        """
        return self.player_comp.SetPlayerNaturalRegen(active)

    def GetGameMode(self):
        # type: () -> int
        """获得游戏模式"""
        return self.game_comp.GetPlayerGameType(self.id)

    def GetOnRideEntity(self):
        # type: () -> str
        """获得正在骑乘生物Id"""
        return self.comp_factory.CreateRide(self.id).GetEntityRider()

    # -----------------------------------------------------------------------------------

    """状态相关"""

    def IsSneaking(self):
        # type: () -> bool
        """是否处于潜行状态"""
        return self.player_comp.isSneaking()

    def IsSwimming(self):
        # type: () -> bool
        """是否处于游泳"""
        return self.player_comp.isSwimming()

    # -----------------------------------------------------------------------------------

    def NotifyToLocalClient(self, event, pack):
        """通知个人客户端事件"""
        system = MDKConfig.GetModuleServer()
        system.NotifyToClient(self.id, event, pack)

    def RunCommand(self, cmd):
        # type: (str) -> None
        """执行指令 - 只有玩家才能"""
        self.comp_factory.CreateCommand(serverApi.GetLevelId()).SetCommand(cmd, self.id)

    # -----------------------------------------------------------------------------------

    """原版背包相关"""

    def GetInventory(self):
        """获取玩家背包"""
        from ..item.inventory import ServerInventoryMgr
        return ServerInventoryMgr(self.id)

    def SpawnItemToInv(self, item, **kwargs):
        # type: (dict, any) -> None
        """生成物品到背包"""
        item_comp = self.comp_factory.CreateItem(serverApi.GetLevelId())
        item_comp.SpawnItemToPlayerInv(item, self.id, kwargs.get("slotPos", -1))

    def SpawnUnbreakableItem(self, item_name, count=1):
        # type: (str, int) -> None
        """获得无法破坏无法丢弃物品"""
        cmd = '/give @s %s %s 0' % (item_name, count)
        cmd += ' {"minecraft:keep_on_death":{}}'
        # cmd += ' {"minecraft:item_lock":{"mode": "lock_in_inventory"}, "minecraft:keep_on_death":{}}'
        self.RunCommand(cmd)

    # -----------------------------------------------------------------------------------

    """属性相关"""

    def SetAttackSpeed(self, speed):
        # type: (float) -> bool
        """设置玩家攻击速度"""
        speed = Misc.GetClamp(speed, 0.5, 2.0)
        return self.player_comp.SetPlayerAttackSpeedAmplifier(speed)

    # -----------------------------------------------------------------------------------

    def GetStepHeight(self):
        # type: () -> float
        """返回玩家前进非跳跃状态下能上的最大台阶高度"""
        return self.attr_comp.GetStepHeight()

    def SetStepHeight(self, height):
        # type: (float) -> bool
        """设置玩家前进非跳跃状态下能上的最大台阶高度\n
        默认值为0.5625，1的话表示能上一个台阶
        """
        return self.attr_comp.SetStepHeight(height)

    def ResetStepHeight(self):
        # type: () -> bool
        """恢复引擎默认玩家前进非跳跃状态下能上的最大台阶高度"""
        return self.attr_comp.ResetStepHeight()

    # -----------------------------------------------------------------------------------

    """重生点相关"""

    def GetPlayerRespawnPos(self):
        # type: () -> (tuple, int)
        """获取玩家复活位置和维度"""
        resDict = self.player_comp.GetPlayerRespawnPos()
        return resDict.get("pos"), resDict.get("dimensionId")

    def SetPlayerRespawnPos(self, pos, dimensionId):
        # type: (tuple, int) -> bool
        """设置玩家复活的位置与维度"""
        return self.player_comp.SetPlayerRespawnPos(pos, dimensionId)

    def SetSpawnDimensionAndPosition(self, dimId, pos):
        # type: (int, tuple) -> bool
        """设置世界出生点维度与坐标"""
        return self.game_comp.SetSpawnDimensionAndPosition(dimId, pos)

    def SaveDimPos(self):
        """保存目前维度的位置"""
        dataKey = MDKConfig.ModuleNamespace + "DimPosStorage"
        storage = self.GetStorage(dataKey)
        storage[self.dim] = self.foot_pos
        self.SetStorage(dataKey, storage)

    def GetDimPos(self, dimId, fix=True):
        # type: (int, bool) -> tuple
        """
        获得目标维度保存的维度坐标\n
        - 需要SaveDimPos保存数据
        - 默认位置提高1.62
        """
        dataKey = MDKConfig.ModuleNamespace + "DimPosStorage"
        storage = self.GetStorage(dataKey)
        to_pos = storage.get(dimId)
        if to_pos and fix:
            return Misc.GetPosModify(to_pos, (0, 1.62, 0))

    def SetSpreadPlayer(self, pos, min_range, max_range):
        # type: (tuple, int, int) -> None
        """随机传送玩家"""
        command_comp = self.comp_factory.CreateCommand(self.id)
        command_comp.SetCommand("/spreadplayers %s %s %s %s @s" % (pos[0], pos[-1], min_range, max_range))

    # -----------------------------------------------------------------------------------

    """信息显示相关"""

    def SetTipMessage(self, msg):
        # type: (str) -> None
        """发送消息给玩家"""
        self.game_comp.SetOneTipMessage(self.id, msg)

    def SetOneNotifyMsg(self, msg):
        # type: (str) -> None
        """设置个人消息通知 - 左上角"""
        self.comp_factory.CreateMsg(self.id).NotifyOneMessage(self.id, msg)

    def SetTitleDisplay(self, msg):
        """指令方式显示标题"""
        command_comp = self.comp_factory.CreateCommand(serverApi.GetLevelId())
        command_comp.SetCommand("/title @s title %s" % msg, self.id)

    def SetSubTitleDisplay(self, title, subtitle):
        """
        指令方式显示标题和副标题\n
        副标题需要标题有内容才显示，不能单独使用
        """
        command_comp = self.comp_factory.CreateCommand(serverApi.GetLevelId())
        command_comp.SetCommand("/title @s title %s" % title, self.id)
        command_comp.SetCommand("/title @s subtitle %s" % subtitle, self.id)

    def SetActionbarDisplay(self, msg):
        """指令方式显示在actionbar"""
        command_comp = self.comp_factory.CreateCommand(serverApi.GetLevelId())
        command_comp.SetCommand("/title @s actionbar %s" % msg, self.id)

    # -----------------------------------------------------------------------------------

    """场景显示相关"""

    def SetFog(self, fogId):
        # type: (str) -> None
        """设置迷雾显示"""
        fogStr = fogId.split(":")[-1]
        comp = self.comp_factory.CreateCommand(serverApi.GetLevelId())
        comp.SetCommand("/fog @s push %s %s" % (fogId, fogStr), self.id)

    def ResetFog(self, fogId):
        # type: (str) -> None
        """重置迷雾显示"""
        fogStr = fogId.split(":")[-1]
        comp = self.comp_factory.CreateCommand(serverApi.GetLevelId())
        comp.SetCommand("/fog @s pop %s" % fogStr, self.id)

    def RemoveFog(self, fogId):
        # type: (str) -> None
        """删除迷雾显示"""
        fogStr = fogId.split(":")[-1]
        comp = self.comp_factory.CreateCommand(serverApi.GetLevelId())
        comp.SetCommand("/fog @s remove %s" % fogStr, self.id)

    # -----------------------------------------------------------------------------------

    """饱食度相关"""

    def AddHunger(self, value):
        # type: (int) -> None
        """增加玩家饥饿值"""
        self.SetHunger(self.GetHunger() + value)

    def SetNaturalStarve(self, active):
        # type: (bool) -> bool
        """
        设置是否开启玩家饥饿掉血\n
        - 当饥饿值小于饥饿临界值时会自动扣除血量
        - 开启饥饿值且开启饥饿掉血时有效.原版默认开启
        """
        return self.player_comp.SetPlayerNaturalStarve(active)

    def GetHunger(self):
        # type: () -> float
        """
        获取玩家饥饿度\n
        - 展示在UI饥饿度进度条上，初始值为20，即每一个鸡腿代表2个饥饿度。
        - 饱和度(saturation) ：玩家当前饱和度，初始值为5
        - 最大值始终为玩家当前饥饿度(hunger)，该值直接影响玩家饥饿度(hunger)。
        - 增加方法：吃食物。
        - 减少方法：每触发一次消耗事件，该值减少1，如果该值不大于0，直接把玩家 饥饿度(hunger) 减少1。
        """
        return self.player_comp.GetPlayerHunger()

    def SetHunger(self, value):
        # type: (float) -> bool
        """设置玩家饥饿值"""
        return self.player_comp.SetPlayerHunger(value)

    def GetStarveLevel(self):
        # type: () -> int
        """
        获取玩家饥饿临界值\n
        - 当饥饿值小于饥饿临界值时会自动扣除血量
        - 开启饥饿值且开启饥饿掉血时有效。原版默认值为1
        """
        return self.player_comp.GetPlayerStarveLevel()

    def SetStarveLevel(self, value):
        # type: (int) -> bool
        """
        设置玩家饥饿临界值\n
        - 当饥饿值小于饥饿临界值时会自动扣除血量
        - 开启饥饿值且开启饥饿掉血时有效。原版默认值为1
        """
        return self.player_comp.SetPlayerStarveLevel(value)

    def GetStarveTick(self):
        # type: () -> int
        """
        获取玩家饥饿掉血速度\n
        - 当饥饿值小于饥饿临界值时会自动扣除血量
        - 开启饥饿值且开启饥饿掉血时有效。原版默认值为80刻（即每4秒）扣除1点血量
        """
        return self.player_comp.GetPlayerStarveTick()

    def SetStarveTick(self, value=80):
        # type: (int) -> bool
        """
        设置玩家饥饿掉血速度\n
        - 当饥饿值小于饥饿临界值时会自动扣除血量
        - 开启饥饿值且开启饥饿掉血时有效
        - 原版默认值为80刻（即每4秒）扣除1点血量
        """
        return self.player_comp.SetPlayerStarveTick(value)

    def GetMaxExhaustionValue(self):
        # type: () -> float
        """
        获取玩家foodExhaustionLevel的归零值，常量值，默认为4。\n
        - 消耗度（exhaustion）是指玩家当前消耗度水平，初始值为0
        - 该值会随着玩家一系列动作（如跳跃）的影响而增加
        - 当该值大于最大消耗度（maxExhaustion）后归零
        - 并且把饱和度（saturation）减少1（为了说明饥饿度机制，我们将此定义为消耗事件）
        """
        return self.player_comp.GetPlayerMaxExhaustionValue()

    def SetMaxExhaustionValue(self, value):
        # type: (float) -> bool
        """
        设置玩家最大消耗度(maxExhaustion)\n
        - 默认值：4.0
        - 通过调整 最大消耗度(maxExhaustion) 的大小
        - 就可以调整 饥饿度(hunger) 的消耗速度
        - 当 最大消耗度(maxExhaustion) 很大时，饥饿度可以看似一直不下降
        """
        return self.player_comp.SetPlayerMaxExhaustionValue(value)

    # -----------------------------------------------------------------------------------

    """经验相关"""

    def AddExp(self, exp):
        # type: (int) -> None
        """增加原版经验"""
        self.comp_factory.CreateExp(self.id).AddPlayerExperience(exp)

    def SetExp(self, exp):
        # type: (int) -> None
        """
        设置原版经验\n
        - 仅仅当前等级的经验
        """
        delta = exp - int(self.GetExp(False))
        if delta:
            self.AddExp(delta)

    def GetExp(self, percent=False):
        # type: (bool) -> float
        """
        获得原版经验\n
        - percent: bool 是否百分比
        """
        return self.comp_factory.CreateExp(self.id).GetPlayerExp(percent)

    def GetTotalExp(self):
        # type: () -> int
        """获得原版全部经验"""
        return self.comp_factory.CreateExp(self.id).GetPlayerTotalExp()

    def SetTotalExp(self, exp):
        # type: (int) -> bool
        """设置原版总经验量"""
        return self.comp_factory.CreateExp(self.id).SetPlayerTotalExp(exp)

    def AddLevel(self, level):
        # type: (int) -> None
        """增加原版等级"""
        self.comp_factory.CreateLv(self.id).AddPlayerLevel(level)

    def GetLevel(self):
        # type: () -> int
        """获得原版等级"""
        return self.comp_factory.CreateLv(self.id).GetPlayerLevel()

    def SetLevel(self, level):
        # type: (int) -> None
        """设置原版等级"""
        delta = level - self.GetLevel()
        if delta:
            self.AddLevel(delta)
