# -*- coding:utf-8 -*-


import weakref

from ...parts.ui.base import LogicBlockUIBase

if __name__ == '__main__':
    from client import LogicBlockCraftTableClient


class LogicBlockCraftTableUI(LogicBlockUIBase):
    """逻辑方块合成台界面"""
    __mVersion__ = 1

    def __init__(self, namespace, name, param):
        super(LogicBlockCraftTableUI, self).__init__(namespace, name, param)
        logic_block = param["logic_block"]
        self.logic_block = weakref.proxy(logic_block)

    def Create(self):
        super(LogicBlockCraftTableUI, self).Create()
        # 绑定实例
        self.LogicBlock.ui = weakref.proxy(self)
        # 界面完成创建
        self.LogicBlock.OnUIFinishedCreate()

    # -----------------------------------------------------------------------------------

    @property
    def LogicBlock(self):
        # type: () -> LogicBlockCraftTableClient
        """逻辑方块"""
        return self.logic_block

    # -----------------------------------------------------------------------------------

    def OnDestroy(self):
        del self.logic_block
        super(LogicBlockCraftTableUI, self).OnDestroy()

    def OnRenderBlockData(self, data):
        # type: (dict) -> None
        """
        渲染方块数据\n
        - 由逻辑方块调用
        """

    def OnFinishedDrag(self, src, des):
        # type: (str, str) -> None
        """
        物品完成拖拽\n
        - src: str 源槽位
        - des: str 目标槽位
        """

    # -----------------------------------------------------------------------------------

    def CheckCanDrag(self, slot):
        # type: (str) -> None
        """
        检测是否可以拖动\n
        - 检测槽位的缓存物品是否可以拖动
        """

    # -----------------------------------------------------------------------------------

    def SetExitUI(self):
        """由逻辑方块执行退出流程"""
        self.LogicBlock.OnUISetExit()
