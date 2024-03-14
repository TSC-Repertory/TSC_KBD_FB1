# -*- coding:utf-8 -*-


from base import UIModuleBase


class PaperDollMgr(UIModuleBase):
    """
    纸娃娃模块管理\n
    - 在uiComponent里直接使用纸娃娃模板，只需渲染实体Id或类型即可
    """
    __mVersion__ = 5

    def __init__(self, ui_node, path, **kwargs):
        super(PaperDollMgr, self).__init__(ui_node, manual_listen=True)
        self._path = path
        self._comp = self.GetNeteasePaperDollUIControl(self._path)

        self._dollRot = 0
        self._lastPos = 0
        self._dollFlag = False
        self._renderId = None

        self._param = {
            "scale": kwargs.get("scale", 0.55),
            "render_depth": kwargs.get("depth", -150),
            "init_rot_y": kwargs.get("init_y", 0.0),
            "rotation": "gesture_x"
        }
        if "molang_dict" in kwargs:
            self._param["molang_dict"] = kwargs["molang_dict"]

        engine_type = kwargs.get("engine_type", "minecraft:player")
        if engine_type and engine_type != "minecraft:player":
            self._param["entity_identifier"] = engine_type
        self._renderId = kwargs.get("entityId")
        if self._renderId:
            self._param["entity_id"] = kwargs["entityId"]
        # -----------------------------------------------------------------------------------
        self.SetActive(True)
        self.Display()

    def OnDestroy(self):
        del self._comp
        del self._param
        super(PaperDollMgr, self).OnDestroy()

    # -----------------------------------------------------------------------------------

    def SetEngineType(self, engine_type):
        # type: (str) -> PaperDollMgr
        """设置渲染实体类型"""
        self._param["entity_identifier"] = engine_type
        self.Display()
        return self

    def SetEntityId(self, entityId):
        # type: (str) -> PaperDollMgr
        """设置渲染实体Id"""
        self._param["entity_id"] = entityId
        self._param["entity_identifier"] = self.comp_factory.CreateEngineType(entityId).GetEngineTypeStr()
        self.Display()
        return self

    def SetScale(self, scale):
        # type: (float) -> PaperDollMgr
        """设置渲染大小"""
        self._param["scale"] = scale
        return self

    def SetRenderDepth(self, depth):
        # type: (int) -> PaperDollMgr
        """
        设置渲染深度\n
        越大可能透视模型
        """
        self._param["render_depth"] = depth
        return self

    def SetInitPos(self, pos):
        # type: (float) -> PaperDollMgr
        """设置初始的旋转y值"""
        self._param["init_rot_y"] = pos
        return self

    def Display(self):
        """显示纸娃娃"""
        if self._renderId:
            self._comp.RenderEntity(self._param)
        else:
            self._comp.RenderSkeletonModel(self._param)
