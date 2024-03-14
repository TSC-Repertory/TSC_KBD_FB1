# -*- coding:utf-8 -*-


import mod.client.extraClientApi as clientApi

from ...common.utils.misc import Algorithm
from ...loader import MDKConfig


class PostProcess(object):

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            instance = super(PostProcess, cls).__new__(cls)
            setattr(cls, "_instance", instance)
            return instance

    def __init__(self):
        self._comp = clientApi.GetEngineCompFactory().CreatePostProcess(clientApi.GetLevelId())
        self.__vignetteActive = False
        self.__gaussianInstance = None

    @classmethod
    def GetSelf(cls):
        if not hasattr(cls, "_instance"):
            PostProcess()
        ins = getattr(cls, "_instance")  # type: PostProcess
        return ins

    # -----------------------------------------------------------------------------------

    def PresetGaussianBlur(self, active):
        self._SetGaussianLerp(-0.5, 1) if active else self._SetGaussianLerp(0.05, 0, reset=True)

    # -----------------------------------------------------------------------------------

    def _SetGaussianBlur(self, active, value=0.1):
        """
        设置高斯模糊效果的模糊半径，半径越大，模糊程度越大，反之则模糊程度越小。
        - radius: float 模糊半径大小，值的范围为[0,10]，小于或大于这个范围的值将被截取为边界值0或10
        """
        if value <= 0:
            active = False
        self._comp.SetEnableGaussianBlur(active)
        if active:
            self._comp.SetGaussianBlurRadius(value)

    def _SetVignette(self, active, value=1.0):
        self._comp.SetEnableVignette(active)
        if active:
            self._comp.SetVignetteSmoothness(value)

    def _SetGaussianLerp(self, start, end, reverse=False, reset=False):
        if reverse:
            start, end = end, start

        def active():
            for value in Algorithm.lerp(start, end, 0.1, error=0.01):
                yield 1
                self._SetGaussianBlur(True, value)

        def _reset():
            self._SetGaussianBlur(False)

        system = MDKConfig.GetModuleClient()
        if self.__gaussianInstance:
            system.StopCoroutine(self.__gaussianInstance)
        self.__gaussianInstance = system.StartCoroutine(active, _reset if reset else None)

    def _IsGaussianOn(self):
        # type: () -> bool
        return self._comp.CheckGaussianBlurEnabled()

    def _IsVignetteOn(self):
        return self.__vignetteActive
