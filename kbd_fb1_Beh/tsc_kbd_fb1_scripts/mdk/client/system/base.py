# -*- coding:utf-8 -*-


import weakref

from ..item.base import ClientItem
from ...client.entity import *
from ...common.system.base import *
from ...common.utils.misc import Misc


class ClientModuleExtend(object):
    """客户端模块拓展"""
    __mVersion__ = 2

    _module_system = None

    @property
    def ModuleSystem(self):
        # type: () -> MDKConfig.GetModuleClientSystemCls()
        if ClientModuleExtend._module_system:
            return ClientModuleExtend._module_system
        ClientModuleExtend._module_system = weakref.proxy(MDKConfig.GetModuleClient())
        return ClientModuleExtend._module_system

    _attr_module = None

    @property
    def AttrModule(self):
        # type: () -> MDKConfig.GetPresetModule().AttrModuleClient
        if ClientModuleExtend._attr_module:
            return ClientModuleExtend._attr_module
        module = self.ModuleSystem.GetModule(MDKConfig.GetPresetModule().AttrModuleClient.GetId())
        if not module:
            return None
        ClientModuleExtend._attr_module = weakref.proxy(module)
        return ClientModuleExtend._attr_module

    _property_module = None

    @property
    def PropertyModule(self):
        # type: () -> MDKConfig.GetPresetModule().PropertyModuleClient
        if ClientModuleExtend._property_module:
            return ClientModuleExtend._property_module
        module = self.ModuleSystem.GetModule(MDKConfig.GetPresetModule().PropertyModuleClient.GetId())
        if not module:
            return None
        ClientModuleExtend._property_module = weakref.proxy(module)
        return ClientModuleExtend._property_module

    _quest_module = None

    @property
    def QuestModule(self):
        # type: () -> MDKConfig.GetPresetModule().QuestModuleClient
        if ClientModuleExtend._quest_module:
            return ClientModuleExtend._quest_module
        module = self.ModuleSystem.GetModule(MDKConfig.GetPresetModule().QuestModuleClient.GetId())
        if not module:
            return None
        ClientModuleExtend._quest_module = weakref.proxy(module)
        return ClientModuleExtend._quest_module

    _particle_module = None

    @property
    def ParticleModule(self):
        # type: () -> MDKConfig.GetPresetModule().ParticleModuleClient
        if ClientModuleExtend._particle_module:
            return ClientModuleExtend._particle_module
        module = self.ModuleSystem.GetModule(MDKConfig.GetPresetModule().ParticleModuleClient.GetId())
        if not module:
            return None
        ClientModuleExtend._particle_module = weakref.proxy(module)
        return ClientModuleExtend._particle_module


class ClientBaseSystem(GameSystem, ClientModuleExtend, ClientRecall):
    """客户端系统基类"""
    __mVersion__ = 18
    _ActiveNode = {}

    def __init__(self, system, *args, **kwargs):
        self.__namespace = clientApi.GetEngineNamespace()
        self.__system_name = clientApi.GetEngineSystemName()

        self.RawEntity = RawEntity
        self.LivingEntity = LivingEntity
        self.ParticleEntity = ParticleEntity
        self.Item = ClientItem

        self.system = system  # type: clientApi.GetClientSystemCls()

        self.comp_factory = clientApi.GetEngineCompFactory()
        self.local_id = clientApi.GetLocalPlayerId()
        self.game_comp = self.comp_factory.CreateGame(clientApi.GetLevelId())
        self.camera_comp = self.comp_factory.CreateCamera(clientApi.GetLocalPlayerId())

        self.add_timer = self.game_comp.AddTimer
        self.local_player = PlayerEntity.GetSelf()
        # -----------------------------------------------------------------------------------
        super(ClientBaseSystem, self).__init__(*args, **kwargs)

    def OnDestroy(self):
        super(ClientBaseSystem, self).OnDestroy()
        del self.system

    def _InitEvent(self):
        self.BatchListenDefault(self.defaultEvent)
        self.BatchListenBaseServer(self.serverEvent)
        self.BatchListenBaseClient(self.clientEvent)
        super(ClientBaseSystem, self)._InitEvent()

    def _DestroyEvent(self):
        self.BatchUnListenDefault(self.defaultEvent)
        self.BatchUnListenBaseServer(self.serverEvent)
        self.BatchUnListenBaseClient(self.clientEvent)
        super(ClientBaseSystem, self)._DestroyEvent()

    # -----------------------------------------------------------------------------------

    def RegisterKeyPressRecall(self, key, recall):
        # type: (int, any) -> None
        """注册按键回调"""
        self.ModuleSystem.RegisterKeyPressRecall(key, recall)

    def UnRegisterKeyPressRecall(self, key, recall):
        # type: (int, any) -> None
        """反注册按键回调"""
        self.ModuleSystem.UnRegisterKeyPressRecall(key, recall)

    # -----------------------------------------------------------------------------------

    def GetDimension(self):
        # type: () -> int
        """获得客户端所在维度"""
        return self.game_comp.GetCurrentDimension()

    def PlayMusic(self, entityId, path, stop=0.0, fadeOut=0.0, loop=False):
        """播放音乐"""
        music_comp = self.comp_factory.CreateCustomAudio(clientApi.GetLevelId())
        musicId = music_comp.PlayCustomMusic(path, (0, 0, 0), entityId=entityId, loop=loop)
        if stop:
            self.game_comp.AddTimer(stop, music_comp.StopCustomMusicById, musicId, fadeOut)
        return musicId

    # -----------------------------------------------------------------------------------

    def GetAimTarget(self):
        # type: () -> dict
        """获得准星选中的生物或方块"""
        return self.camera_comp.PickFacing()

    def GetAimEntity(self):
        # type: () -> str
        """获得准星选中的生物"""
        pickData = self.GetAimTarget()
        if pickData.get("type") == "Entity":
            return pickData.get("entityId")
        return ""

    def GetAimBlock(self):
        # type: () -> dict
        """获得准星选中的方块信息"""
        pickData = self.GetAimTarget()
        if pickData.get("type") == "Block":
            return {
                "pos": (pickData.get("x"), pickData.get("y"), pickData.get("z")),
                "face": pickData.get("face")
            }
        return {}

    def GetAimPos(self):
        """获得准星瞄准的位置"""
        pickData = self.GetAimTarget()
        aimType = pickData.get("type")
        if aimType == "None":
            return None
        elif aimType == "Entity":
            pos = self.comp_factory.CreatePos(pickData.get("entityId")).GetFootPos()
            return pos
        elif aimType == "Block":
            return pickData.get("x"), pickData.get("y"), pickData.get("z")

    # -----------------------------------------------------------------------------------

    def GetPlayerStorage(self, modKey):
        # type: (str) -> dict
        """
        获得玩家模组数据\n
        - 需要服务端同步
        """
        return self.local_player.GetStorage(modKey)

    def GetPlayerStorageData(self, modKey, key):
        # type: (str, str) -> any
        """
        获得玩家模组数据特定键的值\n
        - 需要服务端同步
        """
        return self.GetPlayerStorage(modKey).get(key)

    def GetDistanceBetweenEntity(self, entityId):
        # type: (str) -> float
        """获得与实体的距离"""
        pos = self.comp_factory.CreatePos(entityId).GetFootPos()
        return self.GetDistanceBetweenPos(pos)

    def GetDistanceBetweenPos(self, pos):
        # type: (tuple) -> float
        """获得与目标位置的距离"""
        pre = self.local_player.GetPos()
        return Misc.GetDistBetween(pos, pre)

    def GetKeyState(self, key):
        # type: (int) -> bool
        """获得按键状态"""
        return self.ModuleSystem.GetKeyState(key)

    # -----------------------------------------------------------------------------------

    def BroadcastEvent(self, event, pack):
        """客户端广播事件"""
        self.system.BroadcastEvent(event, pack)

    def NotifyToServer(self, event, pack):
        """通知服务端事件"""
        self.system.NotifyToServer(event, pack)

    # -----------------------------------------------------------------------------------

    def SetPopupNotice(self, msg, title):
        """标题弹框"""
        self.game_comp.SetPopupNotice(msg, title)

    def SetTipMessage(self, msg):
        """提示弹框"""
        self.game_comp.SetTipMessage(msg)

    # -----------------------------------------------------------------------------------

    def BatchListenDefault(self, events):
        # type: (any, dict) -> None
        for event, recall in events.iteritems():
            if isinstance(recall, tuple):
                self.ListenDefaultEvent(event, recall[0], recall[1])
            else:
                self.ListenDefaultEvent(event, recall)

    def BatchListenBaseServer(self, events):
        # type: (any, dict) -> None
        for event, recall in events.iteritems():
            if isinstance(recall, tuple):
                self.ListenBaseServer(event, recall[0], recall[1])
            else:
                self.ListenBaseServer(event, recall)

    def BatchListenBaseClient(self, events):
        # type: (any, dict) -> None
        for event, recall in events.iteritems():
            if isinstance(recall, tuple):
                self.ListenBaseClient(event, recall[0], recall[1])
            else:
                self.ListenBaseClient(event, recall)

    def BatchUnListenDefault(self, events):
        # type: (any, dict) -> None
        for event, recall in events.iteritems():
            if isinstance(recall, tuple):
                self.UnListenDefaultEvent(event, recall[0], recall[1])
            else:
                self.UnListenDefaultEvent(event, recall)

    def BatchUnListenBaseServer(self, events):
        # type: (any, dict) -> None
        for event, recall in events.iteritems():
            if isinstance(recall, tuple):
                self.UnListenBaseServer(event, recall[0], recall[1])
            else:
                self.UnListenBaseServer(event, recall)

    def BatchUnListenBaseClient(self, events):
        # type: (any, dict) -> None
        for event, recall in events.iteritems():
            if isinstance(recall, tuple):
                self.UnListenBaseClient(event, recall[0], recall[1])
            else:
                self.UnListenBaseClient(event, recall)

    # -----------------------------------------------------------------------------------

    def ListenDefaultEvent(self, event, recall, priority=0):
        self.system.ListenForEvent(self.__namespace, self.__system_name, event, recall.im_self, recall, priority)

    def ListenBaseServer(self, event, recall, priority=0):
        self.system.ListenForEvent(MDKConfig.ModuleNamespace, MDKConfig.ServerSysName, event, recall.im_self, recall,
                                   priority)

    def ListenBaseClient(self, event, recall, priority=0):
        self.system.ListenForEvent(MDKConfig.ModuleNamespace, MDKConfig.ClientSysName, event, recall.im_self, recall,
                                   priority)

    def UnListenDefaultEvent(self, event, recall, priority=0):
        self.system.UnListenForEvent(self.__namespace, self.__system_name, event, recall.im_self, recall, priority)

    def UnListenBaseServer(self, event, recall, priority=0):
        self.system.UnListenForEvent(MDKConfig.ModuleNamespace, MDKConfig.ServerSysName, event, recall.im_self, recall,
                                     priority)

    def UnListenBaseClient(self, event, recall, priority=0):
        self.system.UnListenForEvent(MDKConfig.ModuleNamespace, MDKConfig.ClientSysName, event, recall.im_self, recall,
                                     priority)

    # ----------------------------------------------------------------------------------

    def GetLocalConfigData(self, key, isGlobal=False):
        # type: (str, bool) -> dict
        """
        获取本地配置文件中存储的数据\n
        - configName: str 配置名称，只能包含字母、数字和下划线字符，另外为了避免addon之间的冲突，建议加上addon的命名空间作为前缀
        - isGlobal: bool 存档配置or全局配置，默认为False
        """
        data = self.comp_factory.CreateConfigClient(clientApi.GetLevelId()).GetConfigData(key, isGlobal)
        if not data:
            return {}
        return Misc.UnicodeConvert(data)

    def SetLocalConfigData(self, key, value, isGlobal=False):
        # type: (str, dict, bool) -> bool
        """
        以本地配置文件的方式存储数据\n
        - configName: str 配置名称，只能包含字母、数字和下划线字符，另外为了避免addon之间的冲突，建议加上addon的命名空间作为前缀
        - value: dict 数据
        - isGlobal: bool 为True时是全局配置，否则为存档配置，默认为False
        """
        return self.comp_factory.CreateConfigClient(clientApi.GetLevelId()).SetConfigData(key, value, isGlobal)

    def UpdateLocalConfigData(self, key, value, isGlobal=False):
        # type: (str, dict, bool) -> bool
        """
        以本地配置文件的方式存储数据\n
        - configName: str 配置名称，只能包含字母、数字和下划线字符，另外为了避免addon之间的冲突，建议加上addon的命名空间作为前缀
        - value: dict 数据
        - isGlobal: bool 为True时是全局配置，否则为存档配置，默认为False
        """
        data = self.GetLocalConfigData(key, isGlobal)
        data.update(value)
        return self.SetLocalConfigData(key, data, isGlobal)

    # -----------------------------------------------------------------------------------

    def AddPickBlackList(self, config):
        # type: (list) -> None
        """添加使用camera组件选取实体时的黑名单，即该实体不会被选取到"""
        for entityId in config:
            self.game_comp.AddPickBlacklist(entityId)

    def ClearPickBlacklist(self):
        # type: () -> bool
        """清除使用camera组件选取实体的黑名单"""
        return self.game_comp.ClearPickBlacklist()

    # -----------------------------------------------------------------------------------

    def StartCoroutine(self, coroutine, recall=None):
        return self.ModuleSystem.StartCoroutine(coroutine, recall)

    def StartCoroutineLine(self, config):
        return self.ModuleSystem.StartCoroutineLine(config)

    def StopCoroutine(self, coroutine, isSafe=False):
        return self.ModuleSystem.StopCoroutine(coroutine, isSafe)

    def GetCoroutine(self, coroutine):
        return self.ModuleSystem.Get(coroutine)

    def DelayTickFunc(self, tick, func):
        # type: (int, any) -> any
        """延迟刻执行"""
        if not callable(func):
            return

        def active():
            yield tick
            func()

        self.StartCoroutine(active)

    # -----------------------------------------------------------------------------------

    def AddUINode(self, ui_key, ui):
        """添加UI结点"""
        self.ModuleSystem.AddUINode(ui_key, ui)

    def DelUINode(self, ui_key):
        """删除UI结点"""
        self.ModuleSystem.DelUINode(ui_key)

    def GetUINode(self, ui_key):
        """
        返回激活的UI结点\n
        未激活时返回None
        """
        return self.ModuleSystem.GetUINode(ui_key)

    def GetAllUINode(self):
        # type: () -> dict
        """获取所有激活的UI结点"""
        return self.ModuleSystem.GetAllUINode()

    def RegisterUI(self, key, config):
        # type: (str, tuple) -> bool
        """注册UI路径"""
        return self.ModuleSystem.RegisterUI(key, config)

    def CheckRegisterUI(self, key):
        # type: (str) -> bool
        """判断ui是否注册"""
        return self.ModuleSystem.CheckRegisterUI(key)

    def GetAllUIConfig(self):
        # type: () -> dict
        """获得所有注册ui"""
        return self.ModuleSystem.GetAllUIConfig()

    def CreateUI(self, key, **param):
        """持久化方式创建UI"""
        config = self.ModuleSystem.GetRegisterUI(key)
        if not config:
            print "[warn]", "ui配置不存在：", key
            return None
        if not param:
            param = {"isHud": 1}
        return clientApi.CreateUI(config[0], config[1], param)

    def PushCreateUI(self, key, param=None):
        """压栈式创建UI"""
        config = self.ModuleSystem.GetRegisterUI(key)
        if not config:
            print "[warn]", "ui配置不存在：", key
            return None
        if not param:
            param = {}
        return clientApi.PushScreen(config[0], config[1], param)

    # -----------------------------------------------------------------------------------

    def GetUIProfile(self):
        """
        获取UI档案模式\n
        - 0: 经典模式
        - 1: Pocket模式
        """
        return self.comp_factory.CreatePlayerView(self.local_id).GetUIProfile()

    @classmethod
    def GetModConfig(cls, path):
        # type: (str) -> dict
        """读取配置内容"""
        return clientApi.GetModConfigJson("modconfigs/" + path)
