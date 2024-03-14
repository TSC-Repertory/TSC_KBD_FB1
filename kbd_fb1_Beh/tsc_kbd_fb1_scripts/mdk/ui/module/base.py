# -*- coding:utf-8 -*-


from ..system.preset import *

"""
UI预设模块编写规范

- 新模块需要继承 <ModUIModuleBaseCls>
- 模块内变量<ui_node> 使用 <UIPreset>实例
"""


class UIModuleBase(ModUIModuleBaseCls):
    """UI模块基类"""
    __mVersion__ = 1

    def __init__(self, ui_node, **kwargs):
        super(UIModuleBase, self).__init__(ui_node, **kwargs)
        self._active = True

    def IsActive(self):
        """模块是否激活"""
        return self._active

    def SetActive(self, isOn):
        # type: (bool) -> None
        """设置模块是否激活"""
        self._active = isOn
