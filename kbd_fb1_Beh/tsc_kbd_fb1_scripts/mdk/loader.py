# -*- coding:utf-8 -*-


import mod.client.extraClientApi as clientApi
import mod.server.extraServerApi as serverApi

from ..modCommon import modConfig

assert modConfig

if __name__ == '__main__':
    from module.system.base import ModuleServerSystem as ServerMainSystem
    from module.system.base import ModuleClientSystem as ClientMainSystem


class MDKConfig(object):
    """MDK通用配置"""
    __MDK_VERSION__ = "0.54.17"
    __SCRIPT_DIR = modConfig.ModEnum.SCRIPT_DIR

    ModuleNamespace = "ModCommonModule_%s" % __SCRIPT_DIR
    ModuleRoot = "%s.mdk.module" % __SCRIPT_DIR
    ServerSysName = ModuleNamespace + "Server"
    ServerClsPath = "%s.system.base.ModuleServerSystem" % ModuleRoot
    ServerConfig = (ModuleNamespace, ServerSysName, ServerClsPath)
    ClientSysName = ModuleNamespace + "Client"
    ClientClsPath = "%s.system.base.ModuleClientSystem" % ModuleRoot
    ClientConfig = (ModuleNamespace, ClientSysName, ClientClsPath)

    _server_ins = None
    _client_ins = None

    @classmethod
    def GetScriptDir(cls):
        # type: () -> str
        """获得脚本根目录"""
        return cls.__SCRIPT_DIR

    @classmethod
    def GetModuleServerSystemCls(cls):
        """获得公用服务端模块系统类"""
        from module.system.base import ModuleServerSystem
        return ModuleServerSystem

    @classmethod
    def GetModuleClientSystemCls(cls):
        """获得公用客户端模块系统类"""
        from module.system.base import ModuleClientSystem
        return ModuleClientSystem

    @classmethod
    def GetModuleServerCls(cls):
        """
        获得服务端模块类\n
        - 用于构建自定义服务端模块
        """
        from module.system.base import ModuleServerBase
        return ModuleServerBase

    @classmethod
    def GetModuleClientCls(cls):
        """
        获得客户端模块类\n
        - 用于构建自定义客户端模块
        """
        from module.system.base import ModuleClientBase
        return ModuleClientBase

    @classmethod
    def GetModuleServer(cls):
        # type: () -> ServerMainSystem
        """获得服务端模块系统"""
        if not cls._server_ins:
            cls._server_ins = serverApi.GetSystem(cls.ModuleNamespace, cls.ServerSysName)
        return cls._server_ins

    @classmethod
    def GetModuleClient(cls):
        # type: () -> ClientMainSystem
        """获得客户端模块系统"""
        if not cls._client_ins:
            cls._client_ins = clientApi.GetSystem(cls.ModuleNamespace, cls.ClientSysName)
        return cls._client_ins

    @classmethod
    def InitModuleServer(cls):
        # type: () -> ServerMainSystem
        """初始化服务端模块系统"""
        system = cls.GetModuleServer()
        if not system:
            system = serverApi.RegisterSystem(*cls.ServerConfig)
        return system

    @classmethod
    def InitModuleClient(cls):
        # type: () -> ClientMainSystem
        """初始化客户端模块系统"""
        system = cls.GetModuleClient()
        if not system:
            system = clientApi.RegisterSystem(*cls.ClientConfig)
        return system

    @classmethod
    def GetPresetModule(cls):
        """获得预设模块"""
        from module import preset_module
        return preset_module

    @classmethod
    def GetMDKVersion(cls):
        # type: () -> str
        """获得MDK版本"""
        return cls.__MDK_VERSION__
