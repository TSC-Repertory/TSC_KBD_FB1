# -*- coding:utf-8 -*-


from base import *


class ClientPresetSystem(clientApi.GetClientSystemCls(), ClientBaseSystem):
    """客户端预设系统"""
    __mVersion__ = 4

    def __init__(self, namespace, system_name):
        super(ClientPresetSystem, self).__init__(namespace, system_name)
        ClientBaseSystem.__init__(self, self)
        # -----------------------------------------------------------------------------------
        self.AddPickBlackList([GameEntity.detector, GameEntity.projectile, GameEntity.particle])

    def Destroy(self):
        self.OnDestroy()

    def SetPaperDollHide(self, isHide=True):
        """设置原版纸娃娃是否显示"""
        self.local_player.SetPaperDollVisible(isHide)
