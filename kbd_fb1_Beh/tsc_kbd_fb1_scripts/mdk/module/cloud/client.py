# -*- coding:utf-8 -*-


from const import *
from ..system.base import *

if __name__ == '__main__':
    from server import CloudModuleServer


class CloudModuleClient(ModuleClientBase):
    """
    云端模块客户端
    - 本模块仅用于联机大厅
    """
    __mVersion__ = 1
    __identifier__ = ModuleEnum.identifier

    def __init__(self):
        super(CloudModuleClient, self).__init__()
        self.rpc = self.ModuleSystem.CreateRpcModule(self, ModuleEnum.identifier)

    def OnDestroy(self):
        self.rpc.Discard()
        del self.rpc
        super(CloudModuleClient, self).OnDestroy()

    @property
    def server(self):
        # type: () -> CloudModuleServer
        return self.rpc
