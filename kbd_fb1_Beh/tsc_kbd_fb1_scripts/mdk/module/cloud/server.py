# -*- coding:utf-8 -*-


from const import *
from ..system.base import *

if __name__ == '__main__':
    from client import CloudModuleClient


class CloudModuleServer(ModuleServerBase):
    """
    云端模块服务端\n
    - 本模块仅用于联机大厅
    """
    __mVersion__ = 1
    __identifier__ = ModuleEnum.identifier

    def __init__(self):
        super(CloudModuleServer, self).__init__()
        self.rpc = self.ModuleSystem.CreateRpcModule(self, ModuleEnum.identifier)

    def OnDestroy(self):
        self.rpc.Discard()
        del self.rpc
        super(CloudModuleServer, self).OnDestroy()

    def ConfigEvent(self):
        super(CloudModuleServer, self).ConfigEvent()
        self.defaultEvent.update({
            ServerEvent.UrgeShipEvent: self.UrgeShipEvent,
            ServerEvent.AddServerPlayerEvent: self.AddServerPlayerEvent,
        })

    # -----------------------------------------------------------------------------------

    @property
    def client(self, target=None):
        # type: (str) -> CloudModuleClient
        return self.rpc(target)

    # -----------------------------------------------------------------------------------

    def UrgeShipEvent(self, args):
        player_id = args["playerId"]

    def AddServerPlayerEvent(self, args):
        player_id = args["id"]
