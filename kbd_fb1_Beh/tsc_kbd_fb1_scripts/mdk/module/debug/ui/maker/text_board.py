# -*- coding:utf-8 -*-


from base import *


class TextBoardMakerScreen(MakerScreenBase):
    """
    文字面板制造界面\n
    """

    def __init__(self, ui_node, **kwargs):
        super(TextBoardMakerScreen, self).__init__(ui_node, **kwargs)
        self.text_comp = self.comp_factory.CreateTextBoard(clientApi.GetLevelId())
        self.text_comp.SetText()
