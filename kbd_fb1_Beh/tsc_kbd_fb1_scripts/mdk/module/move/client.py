# -*- coding:utf-8 -*-


from const import *
from ..system.base import *

if __name__ == '__main__':
    from server import MoveModuleServer


class MoveModuleClient(ModuleClientBase):
    """运动模块客户端"""
    __mVersion__ = 1
    __identifier__ = ModuleEnum.identifier

    def __init__(self):
        super(MoveModuleClient, self).__init__()
        self.rpc = self.ModuleSystem.CreateRpcModule(self, ModuleEnum.identifier)

    def OnDestroy(self):
        self.rpc.Discard()
        del self.rpc
        super(MoveModuleClient, self).OnDestroy()

    @property
    def server(self):
        # type: () -> MoveModuleServer
        return self.rpc
