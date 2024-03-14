# -*- coding:utf-8 -*-


from const import *
from ...module.system.base import *
from ...server.entity import *

if __name__ == '__main__':
    from client import ParticleModuleClient


class ParticleModuleServer(ModuleServerBase):
    """粒子模块服务端"""
    __mVersion__ = 4
    __identifier__ = ModuleEnum.identifier

    def __init__(self):
        super(ParticleModuleServer, self).__init__()
        self.duration_effect = {}

        self.rpc = self.ModuleSystem.CreateRpcModule(self, ModuleEnum.identifier)

    def OnDestroy(self):
        self.rpc.Discard()
        del self.rpc
        super(ParticleModuleServer, self).OnDestroy()

    @property
    def client(self, target=None):
        # type: (str) -> ParticleModuleClient
        return self.rpc(target)

    def ConfigEvent(self):
        super(ParticleModuleServer, self).ConfigEvent()
        self.defaultEvent.update({
            ServerEvent.EntityRemoveEvent: self.EntityRemoveEvent
        })
        self.clientEvent.update({
            ModuleEvent.ModuleRequestDurationParticleEvent: self.ModuleRequestDurationParticleEvent
        })

        # -----------------------------------------------------------------------------------

    """Api"""

    def CreateDurationEffect(self, pos, dim, **kwargs):
        """创建持久化粒子"""
        particle = ParticleEntity.Create(GameEntity.particle, pos=pos, dim=dim)
        if particle:
            particle.SetModel(kwargs["model"])
            particle.SetFixBind(kwargs["path"], kwargs["name"], kwargs["binder"])
            particle.SetDurationType()
            self.duration_effect[particle.id] = particle
            return particle
        print "[error]", "创建持久化粒子失败"

    # -----------------------------------------------------------------------------------

    def EntityRemoveEvent(self, args):
        entityId = args["id"]
        if entityId in self.duration_effect:
            self.duration_effect.pop(entityId, None)

    def ModuleRequestDurationParticleEvent(self, args):
        playerId = args["playerId"]
        entityId = args["entityId"]
        if entityId not in self.duration_effect:
            print "[warn]", "不存在的粒子实体：%s" % entityId
            return
        particle = self.duration_effect[entityId]  # type: ParticleEntity
        particle.PlayAlone(playerId)
