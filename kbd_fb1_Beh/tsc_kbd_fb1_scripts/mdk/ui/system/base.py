# -*- coding:utf-8 -*-


from functools import wraps

from ..base.control import *


def cd_filter(func):
    @wraps(func)
    def warped(*args, **kwargs):
        ui_node, pack = args
        if isinstance(ui_node, ModUIModuleBaseCls) and ui_node.CheckButtonCd(pack["ButtonPath"]):
            func(*args, **kwargs)

    return warped


class ModUIModuleBaseCls(ModUIMoveControlCls, ClientBaseSystem):
    """UI模块基类"""
    __mVersion__ = 4

    def __init__(self, ui_node, **kwargs):
        system = MDKConfig.GetModuleClient()
        kwargs["manual_listen"] = kwargs.get("manual_listen", False)  # 手动启动监听
        ModUIMoveControlCls.__init__(self, ui_node)
        ClientBaseSystem.__init__(self, system, **kwargs)

        self._button_cd = {}

        # 模块暂存数据
        self.dataTemp = 0
        self.dataList = []
        self.dataDict = {}

    def OnDestroy(self):
        del self.dataList
        del self.dataDict
        ClientBaseSystem.OnDestroy(self)
        self.DestroyUI()

    # -----------------------------------------------------------------------------------

    def IsButtonCd(self, path):
        # type: (str) -> bool
        """按钮是否在冷却"""
        return self._button_cd.get(path) is True

    def AddButtonCd(self, path, cd=0.1):
        # type: (str, float) -> None
        """添加按钮CD"""
        self._button_cd[path] = True
        self.add_timer(cd, lambda: self._button_cd.pop(path, None))

    def CheckButtonCd(self, path, cd=0.1):
        # type: (str, float) -> bool
        """
        判断是否可点击状态\n
        - 可点击下返回True 并将按钮置cd
        """
        if self.IsButtonCd(path):
            return False
        self.AddButtonCd(path, cd)
        return True
