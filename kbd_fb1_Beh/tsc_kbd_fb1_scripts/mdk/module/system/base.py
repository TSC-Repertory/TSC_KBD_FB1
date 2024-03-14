# -*- coding:utf-8 -*-


import copy
import weakref

from mod.common.minecraftEnum import KeyBoardType

from parser import GameParser
from ...client.system.preset import ClientPresetSystem, ClientBaseSystem
from ...client.utils.coroutine import CoroutineMgr as ClientCoroutineMgr
from ...common.system.base import *
from ...server.system.preset import ServerPresetSystem, ServerBaseSystem
from ...server.utils.coroutine import CoroutineMgr as ServerCoroutineMgr


class Register(object):
    """注册器"""

    def __init__(self, system):
        if not system:
            print "[error]", "模块系统尚未启动"
            return
        self.system = weakref.proxy(system)  # type: ModuleBaseSystem

    def RegisterModule(self, new_module_cls):
        """注册模块"""
        try:
            module_id = new_module_cls.GetId()
        except AttributeError:
            print "[error]", "无效模块类格式"
            return False
        pre_module_cls = self.system.GetModuleCls(module_id)
        """版本检测"""
        if not pre_module_cls:
            self.system.SetModuleCls(module_id, new_module_cls)
            # print "[info]", "首次注册模块：%s <version-%s>" % (module_id, new_module_cls.GetVersion())
            return True
        if pre_module_cls.GetVersion() < new_module_cls.GetVersion():
            # print "[info]", "注册新版模块：%s <version-%s>" % (module_id, new_module_cls.GetVersion())
            self.system.SetModuleCls(module_id, new_module_cls)
            return True

        # print "[info]", "注册模块失败：%s 存在相同或更高版本 <version-%s>" % (module_id, pre_module_cls.GetVersion())
        return False

    def UnRegisterModule(self, module_key):
        """反注册模块"""
        self.system.DelModuleCls(module_key)


# -----------------------------------------------------------------------------------

class ModuleBaseSystem(object):
    """模块系统"""
    __mVersion__ = 5

    def __init__(self):
        self._sec = 0
        self._update_sec_recall = set()
        self._register = Register(self)

        self._module_cls = {}  # moduleId: module_cls
        self._module_ins = {}  # moduleId: moduleIns

    def Update(self):
        self._sec += 1
        if self._sec >= 30:
            self._sec = 0
            for func in list(self._update_sec_recall):
                func()

    def DestroyCache(self):
        del self._module_cls
        for module_key in self._module_ins.keys():
            module = self._module_ins.pop(module_key, None)
            module.OnDestroy()
            del module
        del self._module_ins

    def GetRegister(self):
        # type: () -> Register
        """获得注册器"""
        return self._register

    # -----------------------------------------------------------------------------------

    def RegisterUpdateSecond(self, recall):
        """注册秒更新回调"""
        self._update_sec_recall.add(recall)

    def UnRegisterUpdateSecond(self, recall):
        """反注册秒更新回调"""
        self._update_sec_recall.discard(recall)

    # -----------------------------------------------------------------------------------

    def HasModule(self, module_key):
        # type: (str) -> bool
        """模块是否已经加载"""
        return module_key in self._module_ins.iterkeys()

    def SetModule(self, module_key, module):
        """设置模块实例"""
        self._module_ins[module_key] = module

    def DelModule(self, module_key):
        """删除模块实例"""
        module = self._module_ins.pop(module_key, None)
        # print "[suc]", "删除模块实例：", module, module.GetId(), module.GetVersion()
        if module:
            module.OnDestroy()

    def GetModule(self, module_key):
        # type: (str) -> ModuleBase
        """获得模块实例"""
        module = self._module_ins.get(module_key)  # type: ModuleBase
        return module

    def GetAllModule(self):
        """获得全部激活模块的Id"""
        return self._module_ins.keys()

    def SetModuleCls(self, module_key, module_cls):
        """设置模块类对应"""
        self._module_cls[module_key] = module_cls

    def GetModuleCls(self, module_key):
        # type: (str) -> ModuleBase
        """获得模块类"""
        return self._module_cls.get(module_key)

    def DelModuleCls(self, module_key):
        """删除模块类"""
        self._module_cls.pop(module_key, None)

    # -----------------------------------------------------------------------------------

    def GetModuleVersion(self, module_key):
        # type: (str) -> int
        """获得模块版本"""
        module = self.GetModule(module_key)
        if not module:
            return 0
        return module.GetVersion()


class ModuleServerSystem(ServerPresetSystem, ModuleBaseSystem):
    """模块系统服务端"""
    __mVersion__ = 6

    def __init__(self, namespace, system_name):
        ServerPresetSystem.__init__(self, namespace, system_name)
        ModuleBaseSystem.__init__(self)
        self.__finished_load_module = False
        self.attr_system = None

        def get_attr():
            self.attr_system = serverApi.GetSystem("attrModSys", "attrSysServer")
            print "[suc]获取", self.attr_system
            print "[info]", "loaded preset server system.<version-%s>" % MDKConfig.GetMDKVersion()
        self.game_comp.AddTimer(0.2, get_attr)

    def ConfigEvent(self):
        self.defaultEvent[ServerEvent.LoadServerAddonScriptsAfter] = self.LoadServerAddonScriptsAfter

    def OnDestroy(self):
        self.DestroyCache()
        super(ModuleServerSystem, self).OnDestroy()

    def Update(self):
        ModuleBaseSystem.Update(self)
        ServerCoroutineMgr.Tick()

    # -----------------------------------------------------------------------------------

    @classmethod
    def CreateRpcModule(cls, mgr, identifier, local_id=None):
        """创建远程过程调用模块"""
        return MDKConfig.GetPresetModule().RpcModuleServer(mgr, identifier, local_id)

    # -----------------------------------------------------------------------------------

    def StartCoroutine(self, coroutine, recall=None):
        return ServerCoroutineMgr.StartCoroutine(coroutine, recall)

    def StartCoroutineLine(self, config):
        return ServerCoroutineMgr.StartCoroutineLine(config)

    def StopCoroutine(self, coroutine, isSafe=False):
        return ServerCoroutineMgr.StopCoroutine(coroutine, isSafe)

    def GetCoroutine(self, coroutine):
        return ServerCoroutineMgr.Get(coroutine)

    # -----------------------------------------------------------------------------------

    def LoadServerAddonScriptsAfter(self, _):
        if self.__finished_load_module:
            return
        module_num = 0
        for module_key, module_cls in self._module_cls.items():
            print "[info]", "active server module:", module_cls.GetId(), module_cls.GetVersion()
            self.SetModule(module_key, module_cls())
            module_num += 1
        self.__finished_load_module = True
        self.BroadcastEvent(ServerEvent.ServerModuleFinishedLoadEvent, {})
        print "[info]", "服务端共加载模块：%s" % module_num


class ModuleClientSystem(ClientPresetSystem, ModuleBaseSystem):
    """模块系统客户端"""
    _ui_instance = {}
    _ui_register = {}
    __mVersion__ = 13

    def __init__(self, namespace, system_name):
        ClientPresetSystem.__init__(self, namespace, system_name)
        ModuleBaseSystem.__init__(self)
        self.__finished_load_module = False
        self._key_state = {}
        self._key_recall_storage = {}
        self._parser = {}

    def OnDestroy(self):
        self.DestroyCache()
        del self._parser
        super(ModuleClientSystem, self).OnDestroy()

    def Update(self):
        ModuleBaseSystem.Update(self)
        ClientCoroutineMgr.Tick()

    def ConfigEvent(self):
        super(ModuleClientSystem, self).ConfigEvent()
        self.defaultEvent.update({
            ClientEvent.LoadClientAddonScriptsAfter: self.LoadClientAddonScriptsAfter,
            ClientEvent.OnKeyPressInGame: self.OnKeyPressInGame,
        })
        self.serverEvent.update({
            ServerEvent.RequestLoadModConfigEvent: self.RequestLoadModConfigEvent,
            ServerEvent.RequestTurnOffUIEvent: self.RequestTurnOffUIEvent,
        })

    # -----------------------------------------------------------------------------------

    @classmethod
    def CreateRpcModule(cls, mgr, identifier):
        """创建远程过程调用模块"""
        return MDKConfig.GetPresetModule().RpcModuleClient(mgr, identifier)

    # -----------------------------------------------------------------------------------

    def SetModConfigParser(self, parser):
        # type: (GameParser) -> None
        """设置配置解析器"""
        key = parser.GetId()
        self._parser[key] = parser

    @classmethod
    def AddUINode(cls, ui_key, ui):
        cls._ui_instance[ui_key] = ui

    @classmethod
    def DelUINode(cls, ui_key):
        ui_node = cls._ui_instance.pop(ui_key, None)
        if ui_node:
            ui_node.OnDestroy()

    @classmethod
    def GetUINode(cls, ui_key):
        return cls._ui_instance.get(ui_key)

    @classmethod
    def GetAllUINode(cls):
        return cls._ui_instance

    @classmethod
    def RegisterUI(cls, key, config):
        # type: (str,dict) -> bool
        """注册UI配置"""
        cls._ui_register[key] = config
        return clientApi.RegisterUI(*config)

    @classmethod
    def CheckRegisterUI(cls, key):
        # type: (str) -> bool
        """判断ui是否注册"""
        return key in cls._ui_register

    @classmethod
    def GetAllUIConfig(cls):
        # type: () -> dict
        """获得所有注册UI"""
        return copy.deepcopy(cls._ui_register)

    @classmethod
    def GetRegisterUI(cls, key):
        # type: (str) -> dict
        """获得注册UI"""
        return cls._ui_register.get(key, {})

    # -----------------------------------------------------------------------------------

    def GetKeyState(self, key):
        # type: (int) -> bool
        """获得按键状态"""
        return self._key_state.get(key, False)

    def RegisterKeyPressRecall(self, key, recall):
        # type: (int, any) -> None
        """注册按键回调"""
        if key not in self._key_recall_storage:
            self._key_recall_storage[key] = set()
        recall_storage = self._key_recall_storage[key]  # type: set
        recall_storage.add(recall)

    def UnRegisterKeyPressRecall(self, key, recall):
        """反注册按键回调"""
        if key not in self._key_recall_storage:
            return
        recall_storage = self._key_recall_storage.get(key)  # type: set
        recall_storage.discard(recall)
        if not recall_storage:
            self._key_recall_storage.pop(key, None)

    # -----------------------------------------------------------------------------------

    def StartCoroutine(self, coroutine, recall=None):
        return ClientCoroutineMgr.StartCoroutine(coroutine, recall)

    def StartCoroutineLine(self, config):
        return ClientCoroutineMgr.StartCoroutineLine(config)

    def StopCoroutine(self, coroutine, isSafe=False):
        return ClientCoroutineMgr.StopCoroutine(coroutine, isSafe)

    def GetCoroutine(self, coroutine):
        return ClientCoroutineMgr.Get(coroutine)

    # -----------------------------------------------------------------------------------

    def RequestLoadModConfigEvent(self, args):
        # type: (dict) -> None
        """
        模块数据配置导入\n
        - 只用在初始化模块时使用
        - 导入完数据会build一次
        """
        pack = {}
        for line in args["config"]:
            config = self.GetModConfig(line)
            name = line.split("/")[-1]
            if name.startswith("root"):
                parser_id = config.get("parser")
                if not parser_id:
                    pack.update(config)
                    continue
                parser = self._parser.get(parser_id)  # type: GameParser
                if not parser:
                    print "[warn]", "Invalid parser: %s" % parser_id
                    continue
                config = parser.Parser(config, line, pack)
                # 数据合并
                if parser.DataMergeMode:
                    for key, value in config.items():
                        if key in pack:
                            pack[key].update(value)
                        else:
                            pack[key] = value
                    continue
            pack.update(config)
        if args.get("parser"):
            parser_id = args["parser"]
            parser = self._parser[parser_id]  # type: GameParser
            pack = parser.Build(pack)
        args["data"] = pack
        self.NotifyToServer(ClientEvent.ResponseLoadModConfigEvent, args)

    def LoadClientAddonScriptsAfter(self, _):
        if self.__finished_load_module:
            return
        module_num = 0
        for module_key, module_cls in self._module_cls.items():
            print "[info]", "active client module:", module_cls.GetId(), module_cls.GetVersion()
            self.SetModule(module_key, module_cls())
            module_num += 1
        self.__finished_load_module = True
        self.BroadcastEvent(ClientEvent.ClientModuleFinishedLoadEvent, {"playerId": self.local_id})
        self.NotifyToServer(ClientEvent.ClientModuleFinishedLoadEvent, {"playerId": self.local_id})
        print "[info]", "客户端共加载模块：%s" % module_num

    @classmethod
    def RequestTurnOffUIEvent(cls, args):
        # type: (dict) -> None
        """
        请求关闭UI界面\n
        - 仅支持使用<PushCreateUI>的界面
        """
        ui_node = args["uiNode"]  # type: str
        top_node = clientApi.GetTopScreen()
        if top_node:
            pre_node = top_node.GetScreenName()
            if pre_node == ui_node:
                clientApi.PopScreen()

    def OnKeyPressInGame(self, args):
        screen_name, is_down, key = super(ModuleClientSystem, self).OnKeyPressInGame(args)
        if key == KeyBoardType.KEY_NUMPAD0:
            self._key_state[key] = is_down
            return
        if not self._key_state.get(KeyBoardType.KEY_NUMPAD0):
            if screen_name != "hud_screen":
                return
        self._key_state[key] = is_down
        if not is_down:
            return
        recall_storage = self._key_recall_storage.get(key)  # type: set
        if recall_storage:
            for recall in list(recall_storage):
                recall()


class ModuleBase(object):
    """模块基类"""
    __mVersion__ = 2  # int: 模块版本
    __identifier__ = "mould"  # str: 模块标识
    __load_data__ = False  # bool: 是否已经导入数据

    def __new__(cls, *args, **kwargs):
        if not cls.__load_data__:
            cls.LoadModuleData()
        return super(ModuleBase, cls).__new__(cls)

    def __del__(self):
        # print "[info]", "del module: %s %s" % (self.GetId(), self.GetVersion())
        pass

    def OnDestroy(self):
        """模块销毁"""

    # -----------------------------------------------------------------------------------

    @classmethod
    def GetVersion(cls):
        # type: () -> int
        """获得模块版本"""
        if not cls.__load_data__:
            cls.LoadModuleData()
        return cls.__mVersion__

    @classmethod
    def GetId(cls):
        # type: () -> str
        """获得模块标识"""
        return cls.__identifier__

    @classmethod
    def LoadModuleData(cls):
        cls.__load_data__ = True


class ModuleServerBase(ServerBaseSystem, ModuleBase):
    """模块服务端"""
    __mVersion__ = 1

    def __init__(self):
        system = MDKConfig.GetModuleServer()
        if not system:
            print "[error]", "模块系统尚未启动"
            return
        ModuleBase.__init__(self)
        ServerBaseSystem.__init__(self, system)


class ModuleClientBase(ClientBaseSystem, ModuleBase):
    """模块客户端"""
    __mVersion__ = 1

    def __init__(self):
        system = MDKConfig.GetModuleClient()
        if not system:
            print "[error]", "模块系统尚未启动"
            return
        ModuleBase.__init__(self)
        ClientBaseSystem.__init__(self, system)
