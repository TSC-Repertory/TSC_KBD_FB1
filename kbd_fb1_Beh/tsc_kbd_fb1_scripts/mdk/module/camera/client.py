# -*- coding:utf-8 -*-


from const import *
from ..system.base import *

if __name__ == '__main__':
    from server import CameraModuleServer


class CameraModuleClient(ModuleClientBase):
    """相机模块客户端"""
    __mVersion__ = 1
    __identifier__ = ModuleEnum.identifier

    def __init__(self):
        super(CameraModuleClient, self).__init__()
        self.rpc = self.ModuleSystem.CreateRpcModule(self, ModuleEnum.identifier)

        self.camera_cache = {}

    def OnDestroy(self):
        self.rpc.Discard()
        del self.rpc
        super(CameraModuleClient, self).OnDestroy()

    def ConfigEvent(self):
        super(CameraModuleClient, self).ConfigEvent()
        self.defaultEvent.update({
            ClientEvent.OnKeyPressInGame: self.OnKeyPressInGame,
        })

    # -----------------------------------------------------------------------------------

    @property
    def server(self):
        # type: () -> CameraModuleServer
        return self.rpc

    # -----------------------------------------------------------------------------------

    def OnKeyPressInGame(self, args):
        screen_name, is_down, key = super(CameraModuleClient, self).OnKeyPressInGame(args)
        if screen_name != "hud_screen" or not is_down:
            return
        is_active = False
        anchor_key = "anchor"
        cache_key = "offset"
        step_key = "step"
        # -----------------------------------------------------------------------------------
        """步长设置"""
        if key == KeyBoardType.KEY_SUBTRACT:
            step = self.camera_cache.get(step_key, 1.0)
            step /= 2.0
            self.camera_cache[step_key] = step
            self.SetTipMessage("step: %s" % step)
        elif key == KeyBoardType.KEY_ADD:
            step = self.camera_cache.get(step_key, 1.0)
            step *= 2.0
            self.camera_cache[step_key] = step
            self.SetTipMessage("step: %s" % step)
        """重置设置"""
        if key == KeyBoardType.KEY_NUMPAD0:
            # 重置
            self.camera_cache[cache_key] = (0, 0, 0)
            self.camera_cache[step_key] = 1.0
            self.camera_cache[anchor_key] = (0, 0, 0)
            is_active = True
        # -----------------------------------------------------------------------------------
        """调整"""
        step = self.camera_cache.get(step_key, 1.0)
        if key == KeyBoardType.KEY_NUMPAD8:
            is_active = True
            cache = list(self.camera_cache.get(cache_key, (0, 0, 0)))
            cache[1] += step
            self.camera_cache[cache_key] = tuple(cache)
        elif key == KeyBoardType.KEY_NUMPAD2:
            is_active = True
            cache = list(self.camera_cache.get(cache_key, (0, 0, 0)))
            cache[1] -= step
            self.camera_cache[cache_key] = tuple(cache)
        elif key == KeyBoardType.KEY_NUMPAD4:
            is_active = True
            cache = list(self.camera_cache.get(cache_key, (0, 0, 0)))
            cache[0] -= step
            self.camera_cache[cache_key] = tuple(cache)
        elif key == KeyBoardType.KEY_NUMPAD6:
            is_active = True
            cache = list(self.camera_cache.get(cache_key, (0, 0, 0)))
            cache[0] += step
            self.camera_cache[cache_key] = tuple(cache)
        elif key == KeyBoardType.KEY_NUMPAD7:
            is_active = True
            cache = list(self.camera_cache.get(cache_key, (0, 0, 0)))
            cache[2] -= step
            self.camera_cache[cache_key] = tuple(cache)
        elif key == KeyBoardType.KEY_NUMPAD9:
            is_active = True
            cache = list(self.camera_cache.get(cache_key, (0, 0, 0)))
            cache[2] += step
            self.camera_cache[cache_key] = tuple(cache)
        # -----------------------------------------------------------------------------------
        """相机分离"""
        if key == KeyBoardType.KEY_HOME:
            config_key = "departure"
            setting = self.camera_cache.get(config_key, True)
            setting = not setting
            self.camera_cache[config_key] = setting
            self.camera_comp.UnDepartCamera() if setting else self.camera_comp.DepartCamera()
        # -----------------------------------------------------------------------------------
        if key == KeyBoardType.KEY_PG_UP:
            is_active = True
            cache = list(self.camera_cache.get(anchor_key, (0, 0, 0)))
            cache[1] += step
            self.camera_cache[anchor_key] = tuple(cache)
        elif key == KeyBoardType.KEY_PG_DOWN:
            is_active = True
            cache = list(self.camera_cache.get(anchor_key, (0, 0, 0)))
            cache[1] -= step
            self.camera_cache[anchor_key] = tuple(cache)
        # -----------------------------------------------------------------------------------
        if is_active:
            offset = self.camera_cache.get(cache_key, (0, 0, 0))
            anchor = self.camera_cache.get(anchor_key, (0, 0, 0))
            text = "offset: %s  anchor: %s" % (offset, anchor)
            self.SetTipMessage(text)
            print "[debug]", "text -> ", text
            self.camera_comp.SetCameraAnchor(anchor)
            self.camera_comp.SetCameraOffset(offset)
