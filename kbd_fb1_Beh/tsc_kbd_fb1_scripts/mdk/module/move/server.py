# -*- coding:utf-8 -*-


from const import *
from ..system.base import *

if __name__ == '__main__':
    from client import MoveModuleClient


class MoveModuleServer(ModuleServerBase):
    """运动模块服务端"""
    __mVersion__ = 1
    __identifier__ = ModuleEnum.identifier

    def __init__(self):
        super(MoveModuleServer, self).__init__()
        self.rpc = self.ModuleSystem.CreateRpcModule(self, ModuleEnum.identifier)

    def OnDestroy(self):
        self.rpc.Discard()
        del self.rpc
        super(MoveModuleServer, self).OnDestroy()

    @property
    def client(self, target=None):
        # type: (str) -> MoveModuleClient
        return self.rpc(target)
