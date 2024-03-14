# -*- coding:utf-8 -*-


from mod.client.system.clientSystem import ClientSystem

from ....client.system.base import *


# 特效基类
class EffectBase(object):
    """特效基类"""
    __mVersion__ = 1

    def __init__(self):
        self.local_id = clientApi.GetLevelId()
        self.system = weakref.proxy(MDKConfig.GetModuleClient())  # type: ClientSystem
        self.comp_factory = clientApi.GetEngineCompFactory()

    # 使用编辑器特效绑定
    def CreateEngineEffectBind(self, path, bind_id, anim):
        # type: (str, str, str) -> int
        """使用编辑器特效绑定"""
        return self.system.CreateEngineEffectBind(path, bind_id, anim)

    # 用于创建粒子特效
    def CreateEngineParticle(self, path, pos):
        """用于创建粒子特效"""
        return self.system.CreateEngineParticle(path, pos)

    # 创建序列帧特效
    def CreateEngineSfx(self, path, pos, rot, scale):
        """创建序列帧特效"""
        return self.system.CreateEngineSfx(path, pos, rot, scale)

    # 根据编辑器参数创建序列帧
    def CreateEngineSfxFromEditor(self, path, pos=None, rot=None, scale=None):
        """根据编辑器参数创建序列帧"""
        return self.system.CreateEngineSfxFromEditor(path, pos, rot, scale)


# 粒子基类
class ParticleBase(EffectBase):
    """粒子基类"""
    __mVersion__ = 1

    def __init__(self, path, pos):
        super(ParticleBase, self).__init__()
        self.id = self.CreateEngineParticle(path, pos)
        self.trans_comp = self.comp_factory.CreateParticleTrans(self.id)
        self.control_comp = self.comp_factory.CreateParticleControl(self.id)

    # -----------------------------------------------------------------------------------

    @property
    # 获得粒子位置
    def pos(self):
        # type: () -> tuple
        """获得粒子位置"""
        return self.trans_comp.GetPos()

    @pos.setter
    # 设置粒子位置
    def pos(self, data):
        # type: (tuple) -> None
        """设置粒子位置"""
        self.trans_comp.SetPos(data)

    @property
    # 获得粒子转向
    def rot(self):
        # type: () -> tuple
        """获得粒子转向"""
        return self.trans_comp.GetRot()

    @rot.setter
    # 设置粒子转向
    def rot(self, data):
        # type: (tuple) -> None
        """设置粒子转向"""
        self.trans_comp.SetRotUseZXY(data)

    # -----------------------------------------------------------------------------------

    """接口相关"""

    # 设置粒子绑定实体
    def BindEntity(self, bind_id, offset, rot, correction=False):
        # type: (str, tuple, tuple, bool) -> bool
        """设置粒子绑定实体"""
        return self.comp_factory.CreateParticleEntityBind(self.id).Bind(bind_id, offset, rot, correction)

    # -----------------------------------------------------------------------------------

    """控制相关"""

    # 播放粒子特效
    def Play(self):
        # type: () -> bool
        """播放粒子特效"""
        return self.control_comp.Play()

    # 暂停播放粒子
    def Pause(self):
        # type: () -> bool
        """暂停播放，粒子定格在当前时刻，再次调用Play时继续播放"""
        return self.control_comp.Pause()

    # 停止粒子播放
    def Stop(self):
        # type: () -> bool
        """停止粒子播放"""
        return self.control_comp.Stop()

    # -----------------------------------------------------------------------------------

    """设置相关"""

    # 设置是否本地坐标系
    def SetRelative(self, relative):
        # type: (bool) -> bool
        """
        设置发射出的粒子使用entity坐标系还是世界坐标系\n
        - 当粒子绑定了entity或骨骼模型时，
        - 与特效编辑器中粒子的 相对挂点运动 选项功能相同。
        """
        return self.control_comp.SetRelative(relative)

    # 设置渲染层级
    def SetLayer(self, layer):
        # type: (int) -> bool
        """
        设置渲染层级\n
        - 粒子默认层级为1，当层级不为1时表示该特效开启特效分层渲染功能。
        - 特效（粒子和帧动画）分层渲染时，层级越高渲染越靠后
        - 层级大的会遮挡层级低的，且同一层级的特效会根据特效的相对位置产生正确的相互遮挡关系。
        """
        return self.control_comp.SetLayer(layer)

    # 设置自动调整透明度距离
    def SetFadeDistance(self, distance):
        # type: (float) -> bool
        """
        设置粒子开始自动调整透明度的距离\n
        - 粒子与摄像机之间的距离小于该值时会自动调整粒子的透明度，距离摄像机越近，粒子越透明
        """
        return self.control_comp.SetFadeDistance(distance)

    # 设置粒子材质的纹理滤波是否使用点滤波方法
    def SetUsePointFiltering(self, enable):
        # type: (bool) -> bool
        """
        设置粒子材质的纹理滤波是否使用点滤波方法\n
        - 默认为使用双线性滤波
        """
        return self.control_comp.SetUsePointFiltering(enable)

    # 设置粒子特效中粒子大小的最小值及最大值
    def SetParticleSize(self, min_size, max_size):
        # type: (tuple, tuple) -> bool
        """
        设置粒子特效中粒子大小的最小值及最大值。
        """
        return self.control_comp.SetParticleSize(min_size, max_size)

    # 获取粒子特效中粒子大小的最大值
    def GetParticleMaxSize(self):
        # type: () -> tuple
        """获取粒子特效中粒子大小的最大值"""
        return self.control_comp.GetParticleMaxSize()

    # 获取粒子特效中粒子大小的最小值
    def GetParticleMinSize(self):
        # type: () -> tuple
        """获取粒子特效中粒子大小的最小值"""
        return self.control_comp.GetParticleMinSize()

    # 设置粒子发射器的体积大小缩放
    def SetParticleVolumeSize(self, scale):
        # type: (tuple) -> bool
        """
        设置粒子发射器的体积大小缩放，不影响单个粒子的尺寸\n
        - 粒子发射器的体积越大，则粒子的发射范围越大。
        """
        return self.control_comp.SetParticleVolumeSize(scale)

    # 获取粒子发射器的体积大小缩放值
    def GetParticleVolumeSize(self):
        # type: () -> tuple
        """获取粒子发射器的体积大小缩放值"""
        return self.control_comp.GetParticleVolumeSize()

    # 设置粒子发射器的粒子容量
    def SetParticleMaxNum(self, num):
        # type: (int) -> bool
        """
        设置粒子发射器的粒子容量\n
        - 即粒子发射器所包含的最大粒子数量。
        - 该数量并不代表目前粒子发射器所发射的粒子数量，如需要增加发射的粒子数量，需同时改变粒子的发射频率。
        """
        return self.control_comp.SetParticleMaxNum(num)

    # 获取粒子发射器包含的最大粒子数量
    def GetParticleMaxNum(self):
        # type: () -> int
        """获取粒子发射器包含的最大粒子数量"""
        return self.control_comp.GetParticleMaxNum()

    # 设置粒子发射器每帧发射粒子的频率
    def SetParticleEmissionRate(self, min_rate, max_rate):
        # type: (float, float) -> bool
        """
        设置粒子发射器每帧发射粒子的频率\n
        - 频率越大则每帧发射的粒子数量越多，但粒子数量不会超过粒子发射器的粒子容量，同时由于性能考虑
        - 每帧发射的粒子数量也不会超过100个。
        """
        return self.control_comp.SetParticleEmissionRate(min_rate, max_rate)

    # 获取粒子发射器每帧发射粒子的频率
    def GetParticleEmissionRate(self):
        # type: () -> tuple
        """获取粒子发射器每帧发射粒子的频率"""
        return self.control_comp.GetParticleEmissionRate()


# 序列帧基类
class FrameBase(EffectBase):
    """序列帧基类"""
    __mVersion__ = 1

    def __init__(self, path, pos, rot, scale):
        super(FrameBase, self).__init__()
        self.id = self.CreateEngineSfx(path, pos, rot, scale)
        self.trans_comp = self.comp_factory.CreateFrameAniTrans(self.id)
        self.control_comp = self.comp_factory.CreateFrameAniControl(self.id)

    @property
    # 获得粒子位置
    def pos(self):
        # type: () -> tuple
        """获得粒子位置"""
        return self.trans_comp.GetPos()

    @pos.setter
    # 设置粒子位置
    def pos(self, data):
        # type: (tuple) -> None
        """设置粒子位置"""
        self.trans_comp.SetPos(data)

    @property
    # 获得粒子转向
    def rot(self):
        # type: () -> tuple
        """获得粒子转向"""
        return self.trans_comp.GetRot()

    @rot.setter
    # 设置粒子转向
    def rot(self, data):
        # type: (tuple) -> None
        """设置粒子转向"""
        self.trans_comp.SetRotUseZXY(data)

    @property
    # 获得序列帧尺寸
    def scale(self):
        # type: () -> tuple
        """获得序列帧尺寸"""
        return self.trans_comp.GetScale()

    @scale.setter
    # 设置序列帧尺寸
    def scale(self, data):
        # type: (tuple) -> None
        """设置序列帧尺寸"""
        self.trans_comp.SetScale(data)

    # -----------------------------------------------------------------------------------

    """接口相关"""

    # 序列帧绑定实体
    def BindEntity(self, entity_id, offset, rot):
        # type: (str, tuple, tuple) -> bool
        """序列帧绑定实体"""
        return self.comp_factory.CreateFrameAniEntityBind(self.id).Bind(entity_id, offset, rot)

    # 序列帧绑定骨骼模型
    def BindSkeleton(self, model_id, bone_id, offset, rot):
        # type: (int, str, tuple, tuple) -> bool
        """序列帧绑定骨骼模型"""
        return self.comp_factory.CreateFrameAniSkeletonBind(self.id).Bind(model_id, bone_id, offset, rot)

    # -----------------------------------------------------------------------------------

    """控制相关"""

    # 播放序列帧
    def Play(self):
        # type: () -> bool
        """播放序列帧"""
        return self.control_comp.Play()

    # 暂停播放
    def Pause(self):
        # type: () -> bool
        """暂停播放，序列帧定格在当前时刻，再次调用Play时继续播放"""
        return self.control_comp.Pause()

    # 停止序列帧
    def Stop(self):
        # type: () -> bool
        """
        停止序列帧\n
        - 不是暂停
        """
        return self.control_comp.Stop()

    # -----------------------------------------------------------------------------------

    """设置相关"""

    # 设置序列帧是否始终朝向摄像机
    def SetFaceCamera(self, enable):
        # type: (bool) -> bool
        """
        设置序列帧是否始终朝向摄像机\n
        - 默认为是
        """
        return self.control_comp.SetFaceCamera(enable)

    # 设置序列帧是否循环播放
    def SetLoop(self, enable):
        # type: (bool) -> bool
        """
        设置序列帧是否循环播放\n
        - 默认为否
        """
        return self.control_comp.SetLoop(enable)

    # 设置序列帧是否透视
    def SetDeepTest(self, enable):
        # type: (bool) -> bool
        """
        设置序列帧是否透视\n
        - 默认为否
        """
        return self.control_comp.SetDeepTest(enable)

    # 设置序列帧渲染层级
    def SetLayer(self, layer):
        # type: (int) -> bool
        """
        设置序列帧渲染层级\n
        - 默认层级为1，当层级不为1时表示该特效开启特效分层渲染功能。
        - 特效（粒子和帧动画）分层渲染时，层级越高渲染越靠后，层级大的会遮挡层级低的，
        - 且同一层级的特效会根据特效的相对位置产生正确的相互遮挡关系。
        """
        return self.control_comp.SetLayer(layer)

    # 设置序列帧混合颜色
    def SetMixColor(self, color):
        # type: (tuple) -> bool
        """
        设置序列帧混合颜色\n
        - color: (float, float, float, float)
        """
        return self.control_comp.SetMixColor(color)

    # 设置序列帧开始自动调整透明度的距离
    def SetFadeDistance(self, distance):
        # type: (float) -> bool
        """
        设置序列帧开始自动调整透明度的距离\n
        - 序列帧与摄像机之间的距离小于该值时会自动调整序列帧的透明度，距离摄像机越近，序列帧越透明
        """
        return self.control_comp.SetFadeDistance(distance)

    # 设置序列帧是否使用点滤波
    def SetUsePointFiltering(self, enable):
        # type: (bool) -> bool
        """设置序列帧是否使用点滤波"""
        return self.control_comp.SetUsePointFiltering(enable)
