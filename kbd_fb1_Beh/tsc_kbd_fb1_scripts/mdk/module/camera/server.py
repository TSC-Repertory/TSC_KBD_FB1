# -*- coding:utf-8 -*-


from const import *
from ..system.base import *

if __name__ == '__main__':
    from client import CameraModuleClient


class CameraModuleServer(ModuleServerBase):
    """相机模块服务端"""
    __mVersion__ = 1
    __identifier__ = ModuleEnum.identifier

    def __init__(self):
        super(CameraModuleServer, self).__init__()
        self.rpc = self.ModuleSystem.CreateRpcModule(self, ModuleEnum.identifier)

    def OnDestroy(self):
        self.rpc.Discard()
        del self.rpc
        super(CameraModuleServer, self).OnDestroy()

    def client(self, target=None):
        # type: (str) -> CameraModuleClient
        return self.rpc(target)

    # -----------------------------------------------------------------------------------

    def Debug(self, player_id):
        # type: (str) -> None
        """测试功能"""
