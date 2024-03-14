# -*- coding:utf-8 -*-


from const import *
from ...client.entity import *
from ...module.system.base import *

if __name__ == '__main__':
    from server import ParticleModuleServer


class ParticleModuleClient(ModuleClientBase):
    """粒子模块客户端"""
    __mVersion__ = 4
    __identifier__ = ModuleEnum.identifier

    def __init__(self):
        super(ParticleModuleClient, self).__init__()
        self.effect_delay = {}
        # 持久化粒子
        self.duration_effect = {}

        self.rpc = self.ModuleSystem.CreateRpcModule(self, ModuleEnum.identifier)

    def OnDestroy(self):
        self.rpc.Discard()
        del self.rpc
        del self.effect_delay
        super(ParticleModuleClient, self).OnDestroy()

    def ConfigEvent(self):
        super(ParticleModuleClient, self).ConfigEvent()
        self.defaultEvent.update({
            ClientEvent.AddEntityClientEvent: self.AddEntityClientEvent,
            ClientEvent.RemoveEntityClientEvent: self.RemoveEntityClientEvent,
        })
        self.serverEvent.update({
            ServerEvent.RequestPlayParticleEvent: self.RequestPlayParticleEvent
        })

        # -----------------------------------------------------------------------------------

    # -----------------------------------------------------------------------------------

    @property
    def server(self):
        # type: () -> ParticleModuleServer
        return self.rpc

    # -----------------------------------------------------------------------------------

    def _PlayParticle(self, args):
        # type: (dict) -> None
        """
        请求播放粒子\n
        - entityId: str
        - path: str
        - method: str
        - duration: float
        """
        entityId = args["entityId"]
        path = args["path"]
        method = args["method"]
        duration = args.get("duration", 5.0)
        model_comp = self.comp_factory.CreateModel(entityId)

        if method == "CreateAtPos":
            # 粒子的位置创建
            pos = args.get("pos", RawEntity.GetPos(entityId))
            self.ParticleEntity.CreateAtPos(path, pos).Destroy(duration)
        elif method == "CreateBind":
            # 粒子的绑定
            bindInfo = args.get("bindInfo", {})
            self.ParticleEntity.CreateBind(path, entityId, **bindInfo).Destroy(duration)
        elif method == "FixBind":
            # 粒子的bind文件挂接
            animName = args.get("animName")
            bindInfo = args.get("bindInfo", {})
            if bindInfo:
                offset = bindInfo.get("offset", (0, 0, 0))
                model_comp.SetModelOffset(offset)
            self.system.CreateEngineEffectBind(path, entityId, animName)

        binder = args.get("binder")
        if binder:
            # 绑定至实体 - 需要相机看到实体
            model_comp.BindEntityToEntity(binder)
        if args.get("model"):
            self._ModelDisplay(args)

    def _ModelDisplay(self, args):
        """
        骨骼模型显示\n
        - entityId: str 操作实体对象
        - opacity: float 透明度比例
        - animName: str 动画名称
        - animSpeed: float 动画播放速度
        - isLoop: bool 是否循环播放
        """
        entityId = args.get("entityId")
        config = args.get("model")  # type: dict

        if not config:
            return

        model_comp = self.comp_factory.CreateModel(entityId)

        # 模型透明度
        if config.get("opacity"):
            model_comp.SetEntityOpacity(config.get("opacity"))
        # -----------------------------------------------------------------------------------
        animName = config.get("animName")
        if not animName:
            return

        # 骨骼模型动画播放速度
        if config.get("animSpeed"):
            model_comp.SetAnimSpeed(animName, config.get("animSpeed"))
        # 是否循环播放
        isLoop = config.get("isLoop", False)
        model_comp.PlayAnim(animName, isLoop)

    # -----------------------------------------------------------------------------------

    def AddEntityClientEvent(self, args):
        entityId = args["id"]
        engineTypeStr = args["engineTypeStr"]
        if entityId in self.effect_delay:
            param = self.effect_delay.pop(entityId, None)
            if engineTypeStr == GameEntity.particle:
                self.duration_effect[entityId] = param
            self._PlayParticle(param)
        if engineTypeStr == GameEntity.particle and entityId not in self.duration_effect:
            self.NotifyToServer(ModuleEvent.ModuleRequestDurationParticleEvent, {
                "playerId": self.local_id,
                "entityId": entityId
            })

    def RequestPlayParticleEvent(self, args):
        # type: (dict) -> None
        entityId = args["entityId"]
        if not self.game_comp.IsEntityAlive(entityId):
            self.effect_delay[entityId] = args
            return
        if args.get("type") == "duration":
            self.duration_effect[entityId] = args
        self._PlayParticle(args)

    def RemoveEntityClientEvent(self, args):
        entityId = args["id"]
        if entityId in self.duration_effect:
            self.duration_effect.pop(entityId, None)
