# -*- coding:utf-8 -*-


import mod.client.extraClientApi as clientApi

from ...common.utils.misc import Misc
from ...loader import MDKConfig


class ParticleEntity(object):
    """客户端粒子基类"""
    __mVersion__ = 4

    def __init__(self, path, atPos=(0, 0, 0)):
        system = MDKConfig.GetModuleClient()
        self.comp_factory = clientApi.GetEngineCompFactory()
        self.id = system.CreateEngineParticle(path, atPos)

        if self.id <= 0:
            print "[error]", "粒子创建失败：%s" % path
            return
        self.controller = self.comp_factory.CreateParticleControl(self.id)
        self.SetState(True)

    def Destroy(self, delay=0.0):
        # type: (float) -> None
        """销毁粒子"""
        if delay < 0:
            print "[debug]", "粒子设置不销毁"
            return
        game_comp = self.comp_factory.CreateGame(clientApi.GetLevelId())
        game_comp.AddTimer(delay, self._Destroy) if delay else self._Destroy()

    def _Destroy(self):
        MDKConfig.GetModuleClient().DestroyEntity(self.id)
        print "[debug]", "粒子清除：", self.id

    # -----------------------------------------------------------------------------------

    @classmethod
    def CreateAtPos(cls, path, atPos=(0, 0, 0)):
        # type: (str, tuple) -> ParticleEntity
        """位置创建粒子"""
        particleEntity = ParticleEntity(path, atPos)
        return particleEntity

    @classmethod
    def CreateBind(cls, path, binder, **kwargs):
        # type: (str, str, any) -> ParticleEntity
        """创建绑定实体的粒子\n
        可传参数：\n
        - offset: tuple(float,float,float)	绑定的偏移量，相对绑定entity脚下中心
        - rot: tuple(float,float,float)	绑定的旋转角度
        - correction: bool	默认不开启，开启后可以使特效的旋转角度准确设置为参照玩家的相对角度
        """
        kwargs.get("offset")
        kwargs.get("rot")
        kwargs.get("correction")
        atPos = clientApi.GetEngineCompFactory().CreatePos(binder).GetPos()
        particleEntity = ParticleEntity(path, atPos)
        particleEntity.SetBind(binder, **kwargs)
        return particleEntity

    # -----------------------------------------------------------------------------------

    def SetBind(self, entityId, **kwargs):
        # type: (str, dict) -> ParticleEntity
        """绑定特效至实体\n
        - offset: tuple(float,float,float)	绑定的偏移量，相对绑定entity脚下中心
        - rot: tuple(float,float,float)	绑定的旋转角度
        - correction: bool	默认不开启，开启后可以使特效的旋转角度准确设置为参照玩家的相对角度
        """
        offset = kwargs.get("offset", (0, 0, 0))
        rot = kwargs.get("rot", (0, 0, 0))
        correction = kwargs.get("correction", True)
        isBind = self.comp_factory.CreateParticleEntityBind(self.id).Bind(entityId, offset, rot, correction)
        if not isBind:
            print "[error]", "粒子绑定失败：%s" % entityId
        return self

    def SetState(self, state):
        # type: (bool) -> ParticleEntity
        """设置粒子播放状态"""
        self.controller.Play() if state else self.controller.Stop()
        return self

    def GetId(self):
        # type: () -> int
        """获得粒子Id"""
        return self.id

    # -----------------------------------------------------------------------------------

    """没什么用的接口，二次用再拓展"""

    def _GetParticleSize(self):
        return self.controller.GetParticleMinSize(), self.controller.GetParticleMaxSize()

    def _GetParticleMaxNum(self):
        return self.controller.GetParticleMaxNum()

    def _GetParticleEmissionRate(self):
        return self.controller.GetParticleEmissionRate()

    def _GetParticleVolumeSize(self):
        return self.controller.GetParticleVolumeSize()

    def _SetParticleSize(self, scale, minSize, maxSize):
        minTuple = Misc.GetTupleFromRate(scale, minSize[:2], minSize[2:])
        maxTuple = Misc.GetTupleFromRate(scale, maxSize[:2], maxSize[2:])
        self.controller.SetParticleSize(minTuple, maxTuple)

    def _SetParticleMaxNum(self, maxNum):
        self.controller.SetParticleMaxNum(maxNum)

    def _SetParticleEmissionRate(self, scale, minTuple, maxTuple):
        minRate = Misc.GetValueFromRate(scale, *minTuple)
        maxRate = Misc.GetValueFromRate(scale, *maxTuple)
        self.controller.SetParticleEmissionRate(minRate, maxRate)

    def _SetParticleVolumeSize(self, scale, sizeTuple):
        pass
        # size = Misc.GetValueFromRate(scale, *sizeTuple)
        # self.controller.SetParticleVolumeSize(tuple(size for _ in xrange(3)))

    @classmethod
    def _ModifyParticleByScale(cls, controller, **kwargs):
        scale = kwargs.get("scale", 1.0)
        if kwargs.get("pSize"):
            cls._SetParticleSize(controller, scale, *kwargs["pSize"])
        if kwargs.get("pNum"):
            controller.SetParticleMaxNum(*kwargs["pNum"])
        if kwargs.get("eRate"):
            cls._SetParticleEmissionRate(controller, scale, *kwargs["eRate"])
        if kwargs.get("vSize"):
            cls._SetParticleVolumeSize(controller, scale, kwargs["vSize"])

    @classmethod
    def _ModifyParticleBindByScale(cls, **kwargs):
        scale = kwargs.get("scale", 1.0)
        newX, newY, newZ = kwargs.get("offset", (0, 0, 0))
        if kwargs.get("rx"):
            newX = Misc.GetValueFromRate(scale, *kwargs["rx"])
        if kwargs.get("ry"):
            newY = Misc.GetValueFromRate(scale, *kwargs["ry"])
        if kwargs.get("rz"):
            newZ = Misc.GetValueFromRate(scale, *kwargs["rz"])
        if kwargs.get("dx"):
            newX = kwargs["dx"]
        if kwargs.get("dy"):
            newY = kwargs["dy"]
        if kwargs.get("dz"):
            newZ = kwargs["dz"]
        kwargs.update({"offset": (newX, newY, newZ)})

        return kwargs
