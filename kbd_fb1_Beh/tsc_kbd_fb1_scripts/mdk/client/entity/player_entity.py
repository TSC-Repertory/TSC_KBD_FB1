# -*- coding:utf-8 -*-


import mod.client.extraClientApi as clientApi
from mod.common.minecraftEnum import OptionId

from living_entity import LivingEntity
from ...loader import MDKConfig


class PlayerEntity(LivingEntity):
    """客户端玩家基类"""
    __mVersion__ = 11
    _localInstance = None
    _newInstance = False

    def __new__(cls, entityId):
        if not cls._newInstance:
            print "[error]", "获取本地玩家实例使用<PlayerEntity.GetSelf>"
            return None
        cls._newInstance = False
        instance = super(PlayerEntity, cls).__new__(cls)
        cls._localInstance = instance
        return instance

    def __init__(self, entityId):
        super(PlayerEntity, self).__init__(entityId)
        level_id = clientApi.GetLevelId()
        self.item_comp = self.comp_factory.CreateItem(self.id)
        self.viewComp = self.comp_factory.CreatePlayerView(self.id)
        self.renderComp = self.comp_factory.CreateActorRender(self.id)
        self.camera_comp = self.comp_factory.CreateCamera(self.id)
        self.playerComp = self.comp_factory.CreatePlayer(self.id)
        self.model_comp = self.comp_factory.CreateModel(self.id)
        self.shop_comp = self.comp_factory.CreateNeteaseShop(level_id)

        self._effects = {}
        self._inventory = {"slot%s" % x: None for x in xrange(36)}

    @classmethod
    def GetSelf(cls):
        # type: () -> PlayerEntity
        """获得本地玩家的实例"""
        if not cls._localInstance:
            cls._newInstance = True
            system = MDKConfig.GetModuleClient()
            if not system:
                return PlayerEntity(clientApi.GetLocalPlayerId())
            cls._localInstance = getattr(system, "playerEntity")
        instance = cls._localInstance  # type: PlayerEntity
        return instance

    # -----------------------------------------------------------------------------------

    @property
    def dim(self):
        # type: () -> int
        """
        获得玩家所在维度\n
        - 仅本地客户端维度
        """
        return self.game_comp.GetCurrentDimension()

    # -----------------------------------------------------------------------------------

    def HideItem(self, visible, mode=0):
        """
        设置是否隐藏玩家的手持物品模型显示\n
        ----\n
        - mode=0时，表示第一人称和第三人称下均隐藏手持物品；
        - mode=1时表示仅隐藏第三人称下的手持物品；
        - mode=2时表示仅隐藏第一人称下的手持物品。默认值为0。填入0,1,2以外的数值会被强制设置为0
        ----\n
        - visible: bool 设置是否显示或隐藏，True表示显示，False表示隐藏
        - mode: int 设置隐藏手持物品在哪一个视角模式生效。
        """
        self.renderComp.SetPlayerItemInHandVisible(visible, mode)

    def IsInWater(self):
        # type: () -> bool
        """是否在水中"""
        return self.playerComp.isInWater()

    def IsSprinting(self):
        # type: () -> bool
        """是否在疾跑"""
        return self.playerComp.isSprinting()

    def IsSneaking(self):
        # type: () -> bool
        """是否潜行"""
        return self.playerComp.isSneaking()

    # -----------------------------------------------------------------------------------

    """行为相关"""

    def SetSprint(self, active):
        """
        设置疾跑状态\n
        - 疾跑需要饱食度达到7以上
        - 停止时直接停止移动
        """
        if active:
            return self.comp_factory.CreateActorMotion(self.id).BeginSprinting()
        return self.comp_factory.CreateActorMotion(self.id).EndSprinting()

    # -----------------------------------------------------------------------------------

    def GetEffect(self):
        # type: () -> {str: (int, int)}
        """
        获取玩家效果字典\n
        格式：{effectName: (effectAmplifier, effectDuration)}
        """
        return self._effects

    def HasEffect(self, name):
        # type: (str) -> bool
        """
        判断玩家是否有该药水效果\n
        - 需要服务端同步数据
        """
        return name in self._effects.iterkeys()

    # -----------------------------------------------------------------------------------

    def SetTipMessage(self, msg):
        # type: (str) -> None
        """
        发送物品栏上方的信息\n
        - 因为加入敏感词判断，该接口频繁调用十分卡顿
        - 频繁需求建议使用自定义ui
        """
        self.game_comp.SetTipMessage(msg)

    def SetPlayerRender(self, active):
        # type: (bool) -> bool
        """设置本地玩家是否渲染"""
        return self.game_comp.SetRenderLocalPlayer(active)

    # -----------------------------------------------------------------------------------

    """相机相关"""

    def GetPerspective(self):
        # type: () -> int
        """
        获得目前视角\n
        - 0：第一人称视角
        - 1：第三人称视角
        - 2：前视第三人称视角
        """
        return self.viewComp.GetPerspective()

    def SetPerspective(self, perspective):
        # type: (int) -> None
        """设置目前视角"""
        self.viewComp.SetPerspective(perspective)

    def LockPerspective(self, is_lock):
        # type: (bool) -> None
        self.viewComp.LockPerspective(is_lock)

    def SetCameraOffset(self, offset):
        """设置相机的偏置"""
        return self.camera_comp.SetCameraOffset(offset)

    def ResetView(self):
        """
        重置玩家相机和切换视角锁定\n
        一般用于客户端销毁时\n
        """
        self.LockPerspective(False)
        self.camera_comp.SetCameraOffset((0, 0, 0))

    def GetFov(self):
        """获得视角值"""
        return self.camera_comp.GetFov()

    def SetFov(self, fov):
        """设置视角值"""
        return self.camera_comp.SetFov(fov)

    # -----------------------------------------------------------------------------------

    def IsSlotEmpty(self, slot):
        # type: (str) -> bool
        """
        是否该槽位为空\n
        - 需要同步玩家背包才起效
        """
        return self._inventory.get(slot) is None

    def GetSelectedItem(self):
        # type: () -> dict
        """获得手持物品"""
        item = self.item_comp.GetCarriedItem(True)
        if not item:
            item = {}
        return item

    def GetSelectedItemName(self):
        # type: () -> str
        """获得手持物品名字"""
        return self.GetSelectedItem().get("newItemName", "")

    def GetOffhandItem(self):
        # type: () -> dict
        """获得副手物品"""
        item = self.item_comp.GetOffhandItem(True)
        if not item:
            return {}
        return item

    def GetOffhandItemName(self):
        # type: () -> str
        """获得副手物品名字"""
        return self.GetOffhandItem().get("newItemName", "")

    def GetInventoryItem(self, itemName):
        # type: (str) -> int
        """获取背包物品数量"""
        return self.GetInventoryCache().get(itemName, 0)

    def GetInventorySlotItem(self, slot):
        # type: (str) -> dict
        """获得槽位物品"""
        item = self._inventory.get(slot)  # type: dict
        if not item:
            return {}
        return item

    def GetInventory(self):
        # type: () -> dict
        """
        获取客户端玩家背包\n
        - 需要同步玩家背包才起效
        """
        return self._inventory

    def GetInventoryCache(self):
        # type: () -> dict
        """
        获得背包缓存\n
        - itemDict: dict
            - newItemName: str
            - count: int
        """
        cache = dict()
        for item in self._inventory.itervalues():
            if isinstance(item, dict):
                item_name = item["newItemName"]
                pre_count = cache.get(item_name, 0)
                cache[item_name] = pre_count + item["count"]
        return cache

    # -----------------------------------------------------------------------------------

    """皮肤相关"""

    def SetSkin(self, path):
        # type: (str) -> None
        """
        设置玩家原版皮肤\n
        - 以textures/models为相对路径
        """

        def active():
            yield 1
            self.model_comp.SetSkin(path)

        MDKConfig.GetModuleClient().StartCoroutine(active)

    def ResetSkin(self):
        """
        重置玩家原版皮肤\n
        - v2.5之后更新接口
        """
        self.model_comp.ResetSkin()

    # -----------------------------------------------------------------------------------

    """设置相关"""

    def SetPaperDollVisible(self, visible):
        # type: (bool) -> None
        """设置纸娃娃可见"""
        self.viewComp.SetToggleOption(OptionId.HIDE_PAPERDOLL, not visible)

    # -----------------------------------------------------------------------------------

    """经验相关"""

    def GetExp(self, percent=False):
        # type: (bool) -> float
        """
        获得原版经验值\n
        - percent: bool 是否百分比
        """
        return self.game_comp.GetPlayerExp(self.id, percent)

    def GetNextExp(self):
        # type: () -> int
        """获得原版下一级需要经验"""
        return self.game_comp.GetPlayerCurLevelExp(self.id)

    def GetTotalExp(self):
        # type: () -> int
        """获得原版全部经验"""
        return self.game_comp.GetPlayerTotalExp(self.id)

    # -----------------------------------------------------------------------------------

    """护甲相关"""

    def GetArmorValue(self):
        # type: () -> int
        """获得原版护甲值"""
        return self.game_comp.GetArmorValue(self.id)

    # -----------------------------------------------------------------------------------

    """商城相关"""

    def HideShopGate(self):
        """隐藏网易商店入口"""
        self.shop_comp.HideShopGate()

    def ShowShopGate(self):
        """显示网易商城入口"""
        self.shop_comp.ShowShopGate()

    def OpenShopWindow(self):
        """
        打开网易商城窗口\n
        - PC端无效（Apollo的PC端请使用商城插件）
        """
        self.shop_comp.OpenShopWindow()

    def CloseShopWindow(self):
        """关闭网易商城窗口"""
        self.shop_comp.CloseShopWindow()

    def OpenItemDetailWindow(self, category, name):
        # type: (str, str) -> None
        """
        打开特定商品的详情界面\n
        - categoryName: str 商品分类名称
        - itemName: str 商品名称
        """
        self.shop_comp.OpenItemDetailWindow(category, name)

    # -----------------------------------------------------------------------------------

    def SetMotion(self, motion):
        # type: (tuple) -> None
        """设置移动向量"""
        self.comp_factory.CreateActorMotion(self.id).SetMotion(motion)

    def SetJumpByMotion(self, power):
        # type: (float) -> None
        """
        设置向上向量\n
        - 客户端同步问题可能导致延迟摔伤
        - 建议使用服务端修改玩家动量
        """
        motion = self.comp_factory.CreateActorMotion(self.id).GetMotion()
        motion = (motion[0], power, motion[2])
        self.SetMotion(motion)
