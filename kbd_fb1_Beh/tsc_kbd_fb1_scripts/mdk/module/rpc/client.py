# -*- coding:utf-8 -*-


from base import *
from const import *
from ...common.utils.misc import Misc


class RpcModuleClient(RpcModule):
    """远程过程调用模块客户端"""
    __mVersion__ = 5

    def __getattribute__(self, item):
        if item.startswith("_") or item in self._rpc_pass_key:
            return super(RpcModuleClient, self).__getattribute__(item)
        self._function.__getattr__(item)
        return self._function

    def __call__(self, *args, **kwargs):
        param = len(args)
        if param == 1:
            self._recall_config = (args[0], kwargs.get("timeout", 5.0))
        elif param == 2:
            self._recall_config = args
        return self._function

    def _InitEvent(self):
        """初始化事件"""
        self._mgr.ListenBaseServer(ModuleEvent.ModuleRpcSynDataEvent, self._ModuleRpcSynDataEvent)

    def _DestroyEvent(self):
        """反监听事件"""
        self._mgr.UnListenBaseServer(ModuleEvent.ModuleRpcSynDataEvent, self._ModuleRpcSynDataEvent)

    def _SynPack(self, pack):
        self._mgr.NotifyToServer(ModuleEvent.ModuleRpcSynDataEvent, pack)

    def _ModifyRecall(self, pack, recall, timeout):
        uid = Misc.CreateUUID()
        self._recall_map[uid] = recall
        pack["client_recall"] = uid
        pack["client_id"] = clientApi.GetLocalPlayerId()
        self._timer_map[uid] = self._mgr.game_comp.AddTimer(timeout, self._DestroyRecall, uid)

    # -----------------------------------------------------------------------------------

    def _ModuleRpcSynDataEvent(self, args):
        # type: (dict) -> None
        if args["identifier"] != self._identifier:
            return
        if "client_recall" in args:
            if args["client_recall"] in self._recall_map:
                recall = self._DestroyRecall(args["client_recall"])
                if recall:
                    recall(args["data"])
            return
        chain_func = args["func"]  # type: str
        if not chain_func:
            return
        functions = chain_func.split(".")
        method = getattr(self._mgr, functions.pop(0))
        for target in functions:
            if not hasattr(method, target):
                print "[warn]", "方法不存在：", chain_func
                continue
            method = getattr(method, target)
        res = method(*args.pop("data"))
        if args.get("server_recall"):
            args["data"] = res
            args["client_id"] = clientApi.GetLocalPlayerId()
            self._SynPack(args)
