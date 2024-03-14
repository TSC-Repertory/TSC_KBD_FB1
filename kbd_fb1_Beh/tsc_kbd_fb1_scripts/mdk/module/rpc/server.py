# -*- coding:utf-8 -*-


from base import *
from const import *
from ...common.utils.misc import Misc


class RpcModuleServer(RpcModule):
    """远程过程调用模块服务端"""
    __mVersion__ = 6

    def __init__(self, mgr, identifier, local_id=None):
        super(RpcModuleServer, self).__init__(mgr, identifier)
        self._target = None
        self._local_id = local_id

    def __call__(self, target, *args, **kwargs):
        self._target = target
        param = len(args)
        if param == 1:
            self._recall_config = (args[0], kwargs.get("timeout", 5.0))
        elif param == 2:
            self._recall_config = args
        return self._function

    def _InitEvent(self):
        self._mgr.ListenBaseClient(ModuleEvent.ModuleRpcSynDataEvent, self._ModuleRpcSynDataEvent)

    def _DestroyEvent(self):
        self._mgr.UnListenBaseClient(ModuleEvent.ModuleRpcSynDataEvent, self._ModuleRpcSynDataEvent)

    def _SynPack(self, pack):
        if not self._target:
            self._mgr.BroadcastToAllClient(ModuleEvent.ModuleRpcSynDataEvent, pack)
        else:
            self._mgr.NotifyToClient(self._target, ModuleEvent.ModuleRpcSynDataEvent, pack)

    def _ModifyRecall(self, pack, recall, timeout):
        uid = Misc.CreateUUID()
        self._recall_map[uid] = recall
        pack["server_recall"] = uid
        self._timer_map[uid] = self._mgr.game_comp.AddTimer(timeout, self._DestroyRecall, uid)

    # -----------------------------------------------------------------------------------

    def _ModuleRpcSynDataEvent(self, args):
        if args["identifier"] != self._identifier:
            return
        if self._local_id and self._local_id != args["__id__"]:
            return
        if "server_recall" in args:
            if args["server_recall"] in self._recall_map:
                recall = self._DestroyRecall(args["server_recall"])
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
        if args.get("client_recall"):
            args["data"] = res
            self._mgr.NotifyToClient(args.pop("client_id"), ModuleEvent.ModuleRpcSynDataEvent, args)
