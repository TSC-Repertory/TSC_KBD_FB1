# -*- coding:utf-8 -*-


from base import ModuleServerBase
from ...common.system.base import *
from ...common.utils.misc import Misc


class LoadConfigModuleServer(ModuleServerBase):
    """导入配置模块服务端"""
    __mVersion__ = 3
    __identifier__ = "mould"
    _ModuleRequestRegisterEvent = ""
    _RegisterDataParser = ""

    def __init__(self):
        super(LoadConfigModuleServer, self).__init__()
        self._load_data = False  # 是否完成数据导入
        self._data_uid = Misc.CreateUUID()

    def ConfigEvent(self):
        super(LoadConfigModuleServer, self).ConfigEvent()
        self.defaultEvent.update({
            ServerEvent.ClientLoadAddonsFinishServerEvent: self._ClientLoadAddonsFinishServerEvent
        })
        self.clientEvent.update({
            ClientEvent.ResponseLoadModConfigEvent: self._ResponseLoadModConfigEvent
        })

    def GetDefaultConfig(self):
        # type: () -> list
        """获得默认配置路径"""
        return []

    # -----------------------------------------------------------------------------------

    def _ClientLoadAddonsFinishServerEvent(self, args):
        self.ClientLoadAddonsFinishServerEvent(args)
        # -----------------------------------------------------------------------------------
        if self._load_data:
            return
        player_id = args["playerId"]
        pack = {"config": self.GetDefaultConfig()}
        self.BroadcastEvent(self._ModuleRequestRegisterEvent, pack)
        # for config in pack["config"]:
        #     print "[info]", "load config <%s> -> %s" % (self.__identifier__, config)
        pack["uid"] = self._data_uid
        pack["parser"] = self._RegisterDataParser
        self.NotifyToClient(player_id, ServerEvent.RequestLoadModConfigEvent, pack)

    def _ResponseLoadModConfigEvent(self, args):
        # type: (dict) -> None
        if self._load_data:
            return
        if args["uid"] != self._data_uid:
            return
        self._load_data = True
        # -----------------------------------------------------------------------------------
        data = args.pop("data", {})
        show = self.OnLoadModConfig(data)
        # -----------------------------------------------------------------------------------
        if show:
            print "[info]", "load config <%s> -> %s" % (self.__identifier__, len(data))
        # -----------------------------------------------------------------------------------
        recall = self.clientEvent.pop(ClientEvent.ResponseLoadModConfigEvent, None)
        self.UnListenBaseClient(ClientEvent.ResponseLoadModConfigEvent, recall)

    # -----------------------------------------------------------------------------------

    def OnLoadModConfig(self, data):
        # type: (dict) -> bool
        """完成配置文件加载"""
        return True
