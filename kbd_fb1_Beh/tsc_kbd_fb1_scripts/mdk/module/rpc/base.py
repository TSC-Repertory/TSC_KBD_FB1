# -*- coding:utf-8 -*-


from ..system.base import *


class RpcModule(object):
    """远程过程调用模块"""
    __mVersion__ = 6
    _rpc_pass_key = ["Discard", "collection_name", "binding_flags", "binding_name"]  # 网易界面退出时会调用

    def __init__(self, mgr, identifier):
        self._mgr = weakref.proxy(mgr)
        self._func_name = None
        self._identifier = identifier  # 调用匹配Id
        self._recall_map = {}
        self._recall_config = {}
        self._timer_map = {}
        self._function = RpcFunction(self)
        self._InitEvent()

    def __getattribute__(self, item):
        # type: (str) -> any
        if item.startswith("_") or item in self._rpc_pass_key:
            return super(RpcModule, self).__getattribute__(item)
        return self._function

    def Discard(self):
        """需要手动销毁"""
        for timer in self._timer_map.values():
            self._mgr.game_comp.CancelTimer(timer)
        del self._timer_map
        del self._recall_map
        del self._function
        self._DestroyEvent()
        del self._mgr

    # -----------------------------------------------------------------------------------

    def _InitEvent(self):
        """初始化事件"""

    def _DestroyEvent(self):
        """反监听事件"""

    # -----------------------------------------------------------------------------------

    def _Trigger(self, function, *args):
        pack = {"data": args, "func": function, "identifier": self._identifier}
        if self._recall_config:
            self._ModifyRecall(pack, *self._recall_config)
            self._recall_config = None
        self._SynPack(pack)

    def _SynPack(self, pack):
        """同步数据"""

    def _ModifyRecall(self, pack, recall, timeout):
        # type: (dict, any, float) -> None
        """修正回调"""

    def _DestroyRecall(self, uid):
        timer = self._timer_map.pop(uid, None)
        if timer:
            self._mgr.game_comp.CancelTimer(timer)
        return self._recall_map.pop(uid, None)

    # -----------------------------------------------------------------------------------

    def _ModuleRpcSynDataEvent(self, args):
        """
        同步事件回调\n
        - identifier: str
        - data: tuple
        - func: str
        - server_recall: str
        - client_recall: str
        - client_id: str
        """


class RpcFunction(object):

    def __init__(self, rpc):
        self._bind_rpc = weakref.proxy(rpc)
        self._rpc_chain = []

    def __getattr__(self, item):
        self._rpc_chain.append(item)
        return self
    
    def __call__(self, *args, **kwargs):
        self._bind_rpc._Trigger(".".join(self._rpc_chain), *args)
        self._rpc_chain = []
