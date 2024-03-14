# -*- coding:utf-8 -*-


import weakref

from ..const import BuffTag
from ...system.base import ServerBaseSystem
from .....mdk.loader import MDKConfig


class Buff(object):
    """增益基类"""
    __mVersion__ = 1

    BUFF_TYPE_ID = ""  # 增益标识
    BUFF_TAG = BuffTag.UnDefine  # 增益标签
    BUFF_IMMUNE_TAG = -1  # 增益免疫标签
    ABILITY = []  # 增益绑定技能

    def __init__(self):
        super(Buff, self).__init__()
        self._cast_dim = 0  # 释放维度
        self._cast_position = (0, 0, 0)  # 释放位置
        self._caster = -1  # 施加者
        self._parent = False  # 当前挂载的目标

        self.buff_layer = 0  # 层数
        self.buff_level = 0  # 等级
        self.buff_duration = 0  # 时长
        self.buff_context = 0  # 上下文

        self._NO_CASTER = False  # 禁用施加者标志

    """接口相关"""

    @classmethod
    def GetBuffTypeId(cls):
        # type: () -> str
        """获得增益标识"""
        return cls.BUFF_TYPE_ID

    # 获得释放维度
    def GetCastDim(self):
        # type: () -> int
        """获得释放维度"""
        return self._cast_dim

    # 获得释放位置
    def GetCastPosition(self):
        # type: () -> tuple
        """获得释放位置"""
        return self._cast_position

    # 获得释放者id
    def GetCaster(self):
        # type: () -> int
        """获得释放者id"""
        if self._NO_CASTER:
            return -1
        return self._caster

    # 获得挂接增益的目标id
    def GetParent(self):
        # type: () -> int
        """获得挂接增益的目标id"""
        return self._parent

    # 获得增益堆叠层数
    def GetBuffLayer(self):
        # type: () -> int
        """获得增益堆叠层数"""
        return self.buff_layer

    # 获得增益等级
    def GetBuffLevel(self):
        # type: () -> int
        """获得增益等级"""
        return self.buff_level

    # 获得增益持续时间
    def GetBuffDuration(self):
        # type: () -> int
        """获得增益持续时间"""
        return self.buff_duration

    # 根据标签驱散增益
    def DispelBuffByTag(self, tag):
        # type: (str) -> None
        """根据标签驱散增益"""

    # 设置无施加者
    def SetNoCaster(self):
        # type: () -> None
        """设置无施加者"""
        self._NO_CASTER = True
        self._caster = -1

    """事件相关"""

    # 增益生效前触发
    def OnBuffAwake(self):
        """增益生效前触发"""

    # 增益生效时触发
    def OnBuffStart(self):
        """增益生效时触发"""

    # 增益刷新流程时触发
    def OnBuffRefresh(self):
        """增益刷新流程时触发"""

    # 增益销毁前
    def OnBuffRemove(self):
        """增益销毁前"""

    # 增益销毁后
    def OnBuffDestroy(self):
        """增益销毁后"""

    # 绑定的技能触发时
    def OnAbilityExecuted(self):
        """绑定的技能触发时"""

    # 造成伤害前触发
    def OnBeforeDealDamage(self):
        """造成伤害前触发"""

    # 造成伤害后触发
    def OnAfterDealDamage(self):
        """造成伤害后触发"""

    # 承受伤害前触发
    def OnBeforeTakeDamage(self):
        """承受伤害前触发"""

    # 承受伤害后触发
    def OnAfterTakeDamage(self):
        """承受伤害后触发"""

    # 目标死亡前触发
    def OnBeforeDead(self):
        """目标死亡前触发"""

    # 目标死亡后触发
    def OnAfterDead(self):
        """目标死亡后触发"""

    # 目标死亡时触发
    def OnKill(self):
        """目标死亡时触发"""


class BuffMgr(ServerBaseSystem):
    """增益管理"""
    __mVersion__ = 1

    def __init__(self, entity_id, *args, **kwargs):
        super(BuffMgr, self).__init__(MDKConfig.GetModuleServer(), *args, **kwargs)
        self.entity_id = entity_id

        # 增益实例数据
        self.buff_storage = {}
        # 标签增益对应
        self.tag_buff_map = {}

    """接口相关"""

    # 加载增益
    def LoadBuff(self, buff_type_id):
        # type: (int) -> bool
        """加载增益"""

    # 增加增益
    def AddBuff(self, buff_ins):
        # type: (Buff) -> bool
        """增加增益"""

    # 删除增益
    def DelBuff(self, buff_ins):
        # type: (Buff) -> bool
        """删除增益"""

    # 删除标签增益
    def DelTagBuff(self, tag):
        # type: (int) -> bool
        """删除标签增益"""

    # 根据Id获得增益
    def GetBuffById(self, buff_id):
        # type: (int) -> any
        """根据Id获得增益"""

    # 根据标签获得增益
    def GetBuffByTag(self, tag):
        # type: (int) -> any
        """根据标签获得增益"""

    # 获得所有增益
    def GetAllBuff(self):
        # type: () -> dict
        """获得所有增益"""

    """数据相关"""

    # 加载增益数据
    def LoadBuffData(self):
        """加载增益数据"""

    # 保存增益数据
    def SaveBuffData(self):
        """保存增益数据"""

    _buff_module = None

    @property
    def BuffModule(self):
        # type: () -> MDKConfig.GetPresetModule().BuffModuleServer
        if BuffMgr._buff_module:
            return BuffMgr._buff_module
        module = self.ModuleSystem.GetModule(MDKConfig.GetPresetModule().BuffModuleServer.GetId())
        if not module:
            return None
        BuffMgr._buff_module = weakref.proxy(module)
        return BuffMgr._buff_module
