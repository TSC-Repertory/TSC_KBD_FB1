# -*- coding:utf-8 -*-


from base import *


class ServerPresetSystem(serverApi.GetServerSystemCls(), ServerBaseSystem):
    """
    服务端系统\n
    建议只存在一个，其他子系统继承<ServerBaseSystem>
    """

    def __init__(self, namespace, system_name):
        super(ServerPresetSystem, self).__init__(namespace, system_name)
        ServerBaseSystem.__init__(self, self)

    def Destroy(self):
        """服务端销毁触发"""
        self.OnDestroy()

    # -----------------------------------------------------------------------------------

    def SetGameRule(self):
        """
        游戏规则
        - option_info
            - pvp: bool 玩家伤害
            - show_coordinates: bool 显示坐标
            - fire_spreads: bool 火焰蔓延
            - tnt_explodes: bool tnt爆炸
            - mob_loot: bool 生物战利品
            - natural_regeneration: bool 自然生命恢复
            - tile_drops: bool 方块掉落
            - immediate_respawn: bool   立即重生
        - cheat_info
            - enable: bool 是否开启作弊
            - always_day: bool 终为白日
            - mob_griefing: bool 生物破坏方块
            - keep_inventory: bool 保留物品栏
            - weather_cycle: bool 天气更替
            - mob_spawn: bool 生物生成
            - entities_drop_loot: bool 实体掉落
            - daylight_cycle: bool 开启昼夜交替
            - command_blocks_enabled: bool 启用方块命令
            - random_tick_speed: int 随机方块tick速度
        """
        # self.game_comp.SetGameRulesInfoServer({})

    def RegisterOnStepOn(self, config):
        # type: (list) -> None
        """注册站立回调方块"""
        for block_name in config:
            self.block_comp.RegisterOnStepOn(block_name, True)
