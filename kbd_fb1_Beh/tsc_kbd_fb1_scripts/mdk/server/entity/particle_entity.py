# -*- coding:utf-8 -*-


from skill_entity import SkillEntity
from ...common.system.base import ServerEvent
from ...loader import MDKConfig


class ParticleEntity(SkillEntity):
    """粒子实例基类"""
    __mVersion__ = 3

    def __init__(self, entityId, **kwargs):
        super(ParticleEntity, self).__init__(entityId)
        self.binder = kwargs.get("binder")
        self.playMode = None
        self.resourcePath = None
        self.resourceKey = None
        self.modelConfig = None
        self.bindInfo = None
        self.effectType = "generic"

    # -----------------------------------------------------------------------------------

    @staticmethod
    def Create(engine_type, **kwargs):
        """粒子实体创建"""
        system = MDKConfig.GetModuleServer()
        atPos, atRot, atDim = kwargs.get("pos"), kwargs.get("rot", (0, 0)), kwargs.get("dim", 0)
        entityId = system.CreateEngineEntityByTypeStr(engine_type, atPos, atRot, atDim)
        if not entityId:
            print "[error]", "创建实体失败: %s" % engine_type
        return ParticleEntity(entityId, **kwargs)

    def SetFixBind(self, path, name, binder=None):
        # type: (str, str, str) -> ParticleEntity
        """
        设置挂点文件式特效绑定\n
        不用维护entity进出视野导致的挂接特效被移除，\n
        引擎会在entity每次进入视野时自动创建所有特效
        """
        self.playMode = "FixBind"
        self.resourcePath = path
        self.resourceKey = name
        if binder:
            self.binder = binder
        return self

    def SetBinder(self, binder):
        # type: (str) -> ParticleEntity
        """设置绑定者"""
        self.binder = binder
        return self

    def SetModelConfig(self, **config):
        """设置骨骼动画配置"""
        self.modelConfig = {
            "opacity": config.get("opacity"),
            "animName": config.get("animName"),
            "animSpeed": config.get("animSpeed"),
            "isLoop": config.get("isLoop", False)
        }

    def SetBindOffset(self, **config):
        """设置绑定位置偏移"""
        self.bindInfo = {
            "offset": config.get("offset")
        }

    def SetBindRot(self):
        """设置绑定旋转偏移"""

    def SetDurationType(self):
        """设置为持久型粒子"""
        self.effectType = "duration"

    # -----------------------------------------------------------------------------------

    def Play(self):
        # type: () -> ParticleEntity
        """同步客户端特效"""
        system = MDKConfig.GetModuleServer()
        system.BroadcastToAllClient(ServerEvent.RequestPlayParticleEvent, {
            "entityId": self.id,
            "method": self.playMode,
            "path": self.resourcePath,
            "animName": self.resourceKey,
            "binder": self.binder,
            "model": self.modelConfig,
            "bindInfo": self.bindInfo,
            "type": self.effectType,
            "_bind": {
                "binder": self.binder,
                "offset": (0, 0, 0),
                "rot": (0, 0, 0)
            }
        })
        return self

    def PlayAlone(self, playerId):
        """对目标客户端播放特效"""
        system = MDKConfig.GetModuleServer()
        system.NotifyToClient(playerId, ServerEvent.RequestPlayParticleEvent, {
            "entityId": self.id,
            "method": self.playMode,
            "path": self.resourcePath,
            "animName": self.resourceKey,
            "binder": self.binder,
            "model": self.modelConfig,
            "bindInfo": self.bindInfo,
            "type": self.effectType,
            "_bind": {
                "binder": self.binder,
                "offset": (0, 0, 0),
                "rot": (0, 0, 0)
            }
        })
