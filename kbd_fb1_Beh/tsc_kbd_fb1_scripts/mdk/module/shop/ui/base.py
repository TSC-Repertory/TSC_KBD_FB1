# -*- coding:utf-8 -*-


from ....ui.system.preset import UIPreset

if __name__ == '__main__':
    from ..server import ShopModuleServer


class ShopModuleUIBase(UIPreset):
    """
    商店模块UI基类\n
    - 商店的服务端一般都可通用
    - UI可根据不同模组变化
    """

    def __init__(self, namespace, name, param):
        super(ShopModuleUIBase, self).__init__(namespace, name, param)
        self.rpc = self.ModuleSystem.CreateRpcModule(self, "shop")

    def OnDestroy(self):
        self.rpc.Discard()
        del self.rpc
        super(ShopModuleUIBase, self).OnDestroy()

    def Create(self):
        super(ShopModuleUIBase, self).Create()
        if self.IsPcNode():
            self.game_comp.SimulateTouchWithMouse(True)

    # -----------------------------------------------------------------------------------

    def server(self):
        # type: () -> ShopModuleServer
        """服务端模块"""
        return self.rpc

    def server_recall(self, recall):
        # type: (any) -> ShopModuleServer
        """服务端模块执行后回调"""
        return self.rpc(recall)
