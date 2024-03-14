# -*- coding:utf-8 -*-


from base import UIModuleBase


class GridMgrBase(UIModuleBase):
    """
    网格管理\n
    - 回收尚未完善
    """
    __mVersion__ = 2

    def __init__(self, ui_node, path, slot_head="grid_slot", **kwargs):
        super(GridMgrBase, self).__init__(ui_node, **kwargs)
        self.slot_head = slot_head
        self.path = path

    def KeyRecallByGridSlotButton(self, args):
        # type: (dict) -> None
        """
        网格按钮回调\n
        - PrevButtonDownID: str
        - TouchPosX: float
        - TouchPosY: float
        - ButtonState: int
        - ButtonPath: str
        - AddTouchEventParams: dict
        - TouchEvent: int
        - #collection_name: str
        - #collection_index: int
        """

    def SetGridVisible(self, visible):
        # type: (bool) -> None
        """控制网格显示"""
        self.GetBaseUIControl(self.path).SetVisible(visible)

    def InitGridScreen(self):
        """
        网格初始化\n
        用于初始化界面时调用
        """
        self.SetGridVisible(True)
        if self.GetBaseUIControl(self.path + "/%s1" % self.slot_head):
            self.UpdateGridRender()
        else:
            def delayUpdateGrid():
                yield 2
                self.InitGridBind()
                self.UpdateGridRender()

            self.StartCoroutine(delayUpdateGrid)

    def InitGridBind(self):
        """网格回调绑定"""

    def UpdateGridRender(self):
        """更新网格槽位渲染"""

    def GetSlotPath(self, slot):
        # type: (int) -> str
        """获得槽位路径"""
        return self.path + "/%s%s" % (self.slot_head, slot)
