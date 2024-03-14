# -*- coding:utf-8 -*-


from ...loader import *


class ServerDefaultEvent(object):
    """服务端原版事件"""
    DamageEvent = "DamageEvent"
    MobDieEvent = "MobDieEvent"
    CommandEvent = "CommandEvent"
    ServerChatEvent = "ServerChatEvent"
    AddServerPlayerEvent = "AddServerPlayerEvent"
    DelServerPlayerEvent = "DelServerPlayerEvent"
    PlayerIntendLeaveServerEvent = "PlayerIntendLeaveServerEvent"
    AddEntityServerEvent = "AddEntityServerEvent"
    EntityRemoveEvent = "EntityRemoveEvent"
    PlayerDieEvent = "PlayerDieEvent"
    PlayerAttackEntityEvent = "PlayerAttackEntityEvent"
    EntityStopRidingEvent = "EntityStopRidingEvent"
    EntityStartRidingEvent = "EntityStartRidingEvent"
    HealthChangeServerEvent = "HealthChangeServerEvent"
    ActuallyHurtServerEvent = "ActuallyHurtServerEvent"
    PlayerEatFoodServerEvent = "PlayerEatFoodServerEvent"
    InventoryItemChangedServerEvent = "InventoryItemChangedServerEvent"
    EntityDefinitionsEventServerEvent = "EntityDefinitionsEventServerEvent"
    ClientLoadAddonsFinishServerEvent = "ClientLoadAddonsFinishServerEvent"
    LoadServerAddonScriptsAfter = "LoadServerAddonScriptsAfter"
    EntityPickupItemServerEvent = "EntityPickupItemServerEvent"
    ServerPlayerTryTouchEvent = "ServerPlayerTryTouchEvent"
    PlayerRespawnFinishServerEvent = "PlayerRespawnFinishServerEvent"
    ActorAcquiredItemServerEvent = "ActorAcquiredItemServerEvent"
    OnScriptTickServer = "OnScriptTickServer"
    ServerPlayerTryDestroyBlockEvent = "ServerPlayerTryDestroyBlockEvent"
    DestroyBlockEvent = "DestroyBlockEvent"
    ServerItemUseOnEvent = "ServerItemUseOnEvent"
    ServerBlockUseEvent = "ServerBlockUseEvent"
    EntityDieLoottableServerEvent = "EntityDieLoottableServerEvent"
    ProjectileDoHitEffectEvent = "ProjectileDoHitEffectEvent"
    ProjectileCritHitEvent = "ProjectileCritHitEvent"
    OnContainerFillLoottableServerEvent = "OnContainerFillLoottableServerEvent"
    PlaceNeteaseStructureFeatureEvent = "PlaceNeteaseStructureFeatureEvent"
    ServerSpawnMobEvent = "ServerSpawnMobEvent"
    DimensionChangeFinishServerEvent = "DimensionChangeFinishServerEvent"
    EntityChangeDimensionServerEvent = "EntityChangeDimensionServerEvent"
    WillTeleportToServerEvent = "WillTeleportToServerEvent"
    AddEffectServerEvent = "AddEffectServerEvent"
    RemoveEffectServerEvent = "RemoveEffectServerEvent"
    RefreshEffectServerEvent = "RefreshEffectServerEvent"
    WillAddEffectServerEvent = "WillAddEffectServerEvent"
    HealthChangeBeforeServerEvent = "HealthChangeBeforeServerEvent"
    ServerEntityTryPlaceBlockEvent = "ServerEntityTryPlaceBlockEvent"
    ExplosionServerEvent = "ExplosionServerEvent"
    PlayerDoInteractServerEvent = "PlayerDoInteractServerEvent"
    StepOnBlockServerEvent = "StepOnBlockServerEvent"
    PistonActionServerEvent = "PistonActionServerEvent"
    ItemReleaseUsingServerEvent = "ItemReleaseUsingServerEvent"
    OnCarriedNewItemChangedServerEvent = "OnCarriedNewItemChangedServerEvent"
    ServerBlockEntityTickEvent = "ServerBlockEntityTickEvent"
    ChunkAcquireDiscardedServerEvent = "ChunkAcquireDiscardedServerEvent"
    ChunkLoadedServerEvent = "ChunkLoadedServerEvent"
    OnOffhandItemChangedServerEvent = "OnOffhandItemChangedServerEvent"
    OnPlayerBlockedByShieldBeforeServerEvent = "OnPlayerBlockedByShieldBeforeServerEvent"
    OnPlayerBlockedByShieldAfterServerEvent = "OnPlayerBlockedByShieldAfterServerEvent"
    BlockRemoveServerEvent = "BlockRemoveServerEvent"
    ChestBlockTryPairWithServerEvent = "ChestBlockTryPairWithServerEvent"
    ServerPlaceBlockEntityEvent = "ServerPlaceBlockEntityEvent"
    GameTypeChangedServerEvent = "GameTypeChangedServerEvent"
    PlayerHurtEvent = "PlayerHurtEvent"
    PlayerTrySleepServerEvent = "PlayerTrySleepServerEvent"
    ServerPostBlockPatternEvent = "ServerPostBlockPatternEvent"
    ServerPreBlockPatternEvent = "ServerPreBlockPatternEvent"
    OnMobHitMobServerEvent = "OnMobHitMobServerEvent"
    NewOnEntityAreaEvent = "NewOnEntityAreaEvent"

    # 联机大厅
    lobbyGoodBuySucServerEvent = "lobbyGoodBuySucServerEvent"
    UrgeShipEvent = "UrgeShipEvent"


class ServerEvent(modConfig.ModServer, ServerDefaultEvent):
    """服务端事件"""
    # 只读事件
    OnUpdateBlockStateEvent = "OnUpdateBlockStateEvent"
    # -----------------------------------------------------------------------------------
    RequestLoadModConfigEvent = "RequestLoadModConfigEvent"  # 请求导入配置文件事件
    RequestRenderEntityEvent = "RequestRenderEntityEvent"  # 请求渲染实体事件
    RequestSetMolangEvent = "RequestSetMolangEvent"  # 请求设置molang事件
    RequestSetRenderEvent = "RequestSetRenderEvent"  # 请求渲染事件
    RequestPlayMusicEvent = "RequestPlayMusicEvent"  # 请求播放音乐事件
    # -----------------------------------------------------------------------------------
    RequestSynchronizeStorageEvent = "RequestSynchronizeStorageEvent"  # 请求数据同步事件
    # -----------------------------------------------------------------------------------
    RequestSetBlockMolangEvent = "RequestSetBlockMolangEvent"  # 请求修改方块Molang事件
    RequestPlayParticleEvent = "RequestPlayParticleEvent"  # 播放特效效果事件
    RequestHideHandItemEvent = "RequestHideHandItemEvent"  # 请求隐藏手持物品事件
    RequestSetSkillCDEvent = "RequestSetSkillCDEvent"  # 请求修改技能CD事件
    RequestTurnOnUIEvent = "RequestTurnOnUIEvent"  # 请求打开UI界面
    RequestTurnOffUIEvent = "RequestTurnOffUIEvent"  # 请求关闭UI界面
    # -----------------------------------------------------------------------------------
    """模块事件"""
    RequestEntityInsEvent = "RequestEntityInsEvent"
    ServerModuleFinishedLoadEvent = "ServerModuleFinishedLoadEvent"  # 服务端模块加载完成事件
    # -----------------------------------------------------------------------------------
    RequestHUDKeyModify = "RequestHUDKeyModify"  # 请求HUD按键调整事件


class ServerPresetRecall(object):
    """服务端预设回调"""

    def OnKeyPressInGame(self, args):
        # type: (dict) -> (str, bool, int)
        """
        客户端按键回调\n
        - playerId: str
        - isDown: str
        - key: str
        """
        return args["playerId"], args["isDown"] == "1", int(args["key"])


class ServerRecall(ServerPresetRecall):
    """服务端回调"""

    def NewOnEntityAreaEvent(self, args):
        # type: (dict) -> None
        """
        触发时机：通过RegisterEntityAOIEvent注册过AOI事件后，当有实体进入或离开注册感应区域时触发该事件。\n
        - name: str 注册感应区域名称
        - enteredEntities: list[str] 进入该感应区域的实体id列表
        - leftEntities: list[str] 离开该感应区域的实体id列表
        """

    def UrgeShipEvent(self, args):
        # type: (dict) -> None
        """
        玩家点击商城催促发货按钮时触发该事件\n
        - playerId: str 玩家id
        """

    def ProjectileCritHitEvent(self, args):
        # type: (dict) -> None
        """
        触发时机：当抛射物与头部碰撞时触发该事件。\n
        注：需调用OpenPlayerCritBox开启玩家爆头后才能触发。\n
        - id: str 子弹id
        - targetId: str 碰撞目标id
        """

    def OnMobHitMobServerEvent(self, args):
        # type: (dict) -> None
        """
        触发时机：通过OpenPlayerHitMobDetection打开生物碰撞检测后，当生物间（包含玩家）碰撞时触发该事件。\n
        注：客户端和服务端分别作碰撞检测，可能两个事件返回的略有差异。\n
        - mobId: str 当前生物的id
        - hittedMobList: list[str] 当前生物碰撞到的其他所有生物id的list
        """

    def lobbyGoodBuySucServerEvent(self, args):
        # type: (dict) -> None
        """
        玩家登录联机大厅服务器，或者联机大厅游戏内购买商品时触发。\n
        如果是玩家登录，触发时玩家客户端已经触发了UiInitFinished事件\n
        - eid: str 购买商品的玩家实体id
        - buyItem: bool 玩家登录时为False，玩家购买了商品时为True
        """

    def ServerPreBlockPatternEvent(self, args):
        # type: (dict) -> None
        """
        触发时机：用方块组合生成生物，在放置最后一个组成方块时触发该事件。\n
        - enable: bool 是否允许继续生成。若设为False，可阻止生成生物
        - x: int 方块x坐标
        - y: int 方块y坐标
        - z: int 方块z坐标
        - dimensionId: int 维度id
        - entityWillBeGenerated: str 即将生成生物的名字，如"minecraft:pig"
        """

    def ServerPostBlockPatternEvent(self, args):
        # type: (dict) -> None
        """
        触发时机：用方块组合生成生物，生成生物之后触发该事件。\n
        - entityId: str 生成生物的id
        - entityGenerated: str 生成生物的名字，如"minecraft:pig"
        - x: int 方块x坐标
        - y: int 方块y坐标
        - z: int 方块z坐标
        - dimensionId: int 维度id
        """

    def PlayerTrySleepServerEvent(self, args):
        # type: (dict) -> None
        """
        玩家尝试使用床睡觉\n
        - playerId: str 玩家id
        - cancel: bool 是否取消（开发者传入）
        """

    def PlayerHurtEvent(self, args):
        # type: (dict) -> None
        """
        触发时机：当玩家受伤害前触发该事件。\n
        - id: str 受击玩家id
        - attacker: str 伤害来源实体id，若没有实体攻击，例如高空坠落，id为-1
        """

    def GameTypeChangedServerEvent(self, args):
        # type: (dict) -> None
        """
        个人游戏模式发生变化时服务端触发。\n
        - playerId: str 玩家Id，SetDefaultGameType接口改变游戏模式时该参数为空字符串
        - oldGameType: int 切换前的游戏模式
        - newGameType: int 切换后的游戏模式
        """

    def ServerPlaceBlockEntityEvent(self, args):
        # type: (dict) -> None
        """
        触发时机：手动放置或通过接口创建含自定义方块实体的方块时触发，此时可向该方块实体中存放数据\n
        - blockName: str 该方块名称
        - dimension: int 该方块所在的维度
        - pos: int 该方块的x坐标
        - pos: int 该方块的y坐标
        - pos: int 该方块的z坐标
        """

    def ChestBlockTryPairWithServerEvent(self, args):
        """
        触发时机：两个并排的小箱子方块准备组合为一个大箱子方块时\n
        - cancel: bool 是否允许触发，默认为False，若设为True，可阻止小箱子组合成为一个大箱子
        - blockX: int 小箱子方块x坐标
        - blockY: int 小箱子方块y坐标
        - blockZ: int 小箱子方块z坐标
        - otherBlockX: int 将要与之组合的另外一个小箱子方块x坐标
        - otherBlockY: int 将要与之组合的另外一个小箱子方块y坐标
        - otherBlockZ: int 将要与之组合的另外一个小箱子方块z坐标
        - dimensionId: int 维度id
        """

    def BlockRemoveServerEvent(self, args):
        # type: (dict) -> None
        """
        触发时机：监听该事件的方块在销毁时触发\n
        可以通过ListenOnBlockRemoveEvent方法进行监听\n
        或者通过json组件netease:listen_block_remove进行配置\n
        - x: int 方块位置x
        - y: int 方块位置y
        - z: int 方块位置z
        - fullName: str 方块的identifier，包含命名空间及名称
        - auxValue: int 方块的附加值
        - dimension: int 该方块所在的维度
        """

    def OnPlayerBlockedByShieldBeforeServerEvent(self, args):
        # type: (dict) -> None
        """
        触发时机：玩家使用盾牌抵挡伤害之前触发\n
        - playerId: str 玩家Id
        - sourceId: str 伤害来源实体Id，没有实体返回"-1"
        - itemDict: dict 盾牌物品字典物品信息字典
        - damage: float 抵挡的伤害数值
        """

    def OnPlayerBlockedByShieldAfterServerEvent(self, args):
        # type: (dict) -> None
        """
        触发时机：玩家使用盾牌抵挡伤害之后触发\n
        - playerId: str 玩家Id
        - sourceId: str 伤害来源实体Id，没有实体返回"-1"
        - itemDict: dict 盾牌物品字典物品信息字典
        - damage: float 抵挡的伤害数值
        """

    def LoadServerAddonScriptsAfter(self, args):
        # type: (dict) -> None
        """服务器加载完mod时触发"""

    def EntityStartRidingEvent(self, args):
        # type: (dict) -> None
        """
        当实体骑乘上另一个实体时触发\n
        - id: str 乘骑者实体id
        - rideId: str 被乘骑者实体id
        """

    def EntityStopRidingEvent(self, args):
        # type: (dict) -> None
        """
        触发时机：当实体停止骑乘时\n
        以下情况不允许取消\n
        ride组件StopEntityRiding接口\n
        玩家传送时\n
        坐骑死亡时\n
        玩家睡觉时\n
        玩家死亡时\n
        未驯服的马\n
        怕水的生物坐骑进入水里\n
        切换维度\n
        - id: str 实体id
        - rideId: str 坐骑id
        - exitFromRider: bool 是否下坐骑
        - entityIsBeingDestroyed: bool 坐骑是否将要销毁
        - switchingRides: bool 是否换乘坐骑
        - cancel: bool 设置为True可以取消（需要与客户端事件一同取消）
        """

    def OnOffhandItemChangedServerEvent(self, args):
        # type: (dict) -> None
        """
        触发时机：玩家切换副手物品时触发该事件\n
        - playerId: str 玩家 entityId
        - oldItemDict: dict/None 旧物品的物品信息字典，当旧物品为空时，此项属性为None
        - newItemDict: dict/None 新物品的物品信息字典，当新物品为空时，此项属性为None
        """

    def ServerBlockUseEvent(self, args):
        # type: (dict) -> None
        """
        触发时机：玩家右键点击新版自定义方块\n
        （或者通过接口AddBlockItemListenForUseEvent增加监听的MC原生游戏方块）时服务端抛出该事件（该事件tick执行，需要注意效率问题）。\n
        - playerId: str 玩家Id
        - blockName: str 方块的identifier，包含命名空间及名称
        - aux: int 方块附加值
        - cancel: bool 设置为True可拦截与方块交互的逻辑。
        - x: int 方块x坐标
        - y: int 方块y坐标
        - z: int 方块z坐标
        - dimensionId: int 维度id
        """

    def ServerBlockEntityTickEvent(self, args):
        # type: (dict) -> None
        """
        触发时机：自定义方块配置了netease:block_entity组件并设tick为true\n
        方块在玩家的模拟距离（新建存档时可以设置，默认为4个区块）内，或者在tickingarea内的时候触发\n
        方块实体的tick事件频率为每秒钟20次\n
        触发本事件时，若正在退出游戏，将无法获取到抛出本事件的方块实体数据（GetBlockEntityData函数返回None），也无法对其进行操作\n
        - blockName: str 该方块名称
        - dimension: int 该方块所在的维度
        - posX: int 该方块的x坐标
        - posY: int 该方块的y坐标
        - posZ: int 该方块的z坐标
        """

    def ItemReleaseUsingServerEvent(self, args):
        # type: (dict) -> None
        """
        触发时机：释放正在使用的物品时\n
        - playerId: str 玩家id
        - durationLeft: float 蓄力剩余时间(当物品缺少"minecraft:maxduration"组件时,蓄力剩余时间为负数)
        - itemDict: dict 使用的物品的物品信息字典
        - maxUseDuration: int 最大蓄力时长
        - cancel: bool 设置为True可以取消，需要同时取消客户端事件ItemReleaseUsingClientEvent
        """

    def OnCarriedNewItemChangedServerEvent(self, args):
        # type: (dict) -> None
        """
        触发时机：玩家切换主手物品时触发该事件\n
        - oldItemDict :dict/None 旧物品的物品信息字典，当旧物品为空时，此项属性为None
        - newItemDict :dict/None 新物品的物品信息字典，当新物品为空时，此项属性为None
        - playerId :str 玩家 entityId
        """

    def StepOnBlockServerEvent(self, args):
        # type: (dict) -> None
        """
        触发时机：实体刚移动至一个新实心方块时触发。\n
        - cancel: bool 是否允许触发，默认为False，若设为True，可阻止触发后续物理交互事件
        - blockX: int 方块x坐标
        - blockY: int 方块y坐标
        - blockZ: int 方块z坐标
        - entityId: str 触发的entity的唯一ID
        - blockName: str 方块的identifier，包含命名空间及名称
        - dimensionId: int 维度id
        """

    def PlayerDoInteractServerEvent(self, args):
        # type: (dict) -> None
        """
        玩家与有minecraft:interact组件的生物交互时触发该事件，例如玩家手持空桶对牛挤奶、玩家手持打火石点燃苦力怕\n
        - playerId: str     玩家Id
        - itemDict: dict    交互时使用物品的物品信息字典
        - interactEntityId: str 交互的生物entityId
        """

    def ChunkAcquireDiscardedServerEvent(self, args):
        # type: (dict) -> None
        """
        服务端区块即将被卸载时触发\n
        - dimension: int 区块所在维度
        - chunkPosX: int 区块的x坐标，对应方块X坐标区间为[x * 16, x * 16 + 15]
        - chunkPosZ: int 区块的z坐标，对应方块Z坐标区间为[z * 16, z * 16 + 15]
        - entities: list(str) 随区块卸载而从世界移除的实体id的列表。注意事件触发时已经无法获取到这些实体的信息，仅供脚本资源回收用。
        - blockEntities: list(dict) 随区块卸载而从世界移除的自定义方块实体的坐标的列表，列表元素dict包含posX，posY，posZ三个int表示自定义方块实体的坐标。注意事件触发时已经无法获取到这些方块实体的信息，仅供脚本资源回收用。
        """

    def ChunkLoadedServerEvent(self, args):
        # type: (dict) -> None
        """
        触发时机：服务端区块加载完成时\n
        - dimension: int 区块所在维度
        - chunkPosX: int 区块的x坐标，对应方块X坐标区间为[x * 16, x * 16 + 15]
        - chunkPosZ: int 区块的z坐标，对应方块Z坐标区间为[z * 16, z * 16 + 15]
        """

    def OnScriptTickServer(self):
        """服务器tick时触发,1秒有30个tick"""

    def ExplosionServerEvent(self, args):
        # type: (dict) -> None
        """
        当发生爆炸时触发。\n
        - blocks: list[[x,y,z,cancel],...] 爆炸涉及到的方块坐标(x,y,z)，cancel是一个bool值
        - victims: list/None 受伤实体id列表，当该爆炸创建者id为None时，victims也为None
        - sourceId: str/None 爆炸创建者id
        - explodePos: list 爆炸位置[x,y,z]
        - dimensionId: int 维度id
        """

    def WillTeleportToServerEvent(self, args):
        # type: (dict) -> None
        """
        实体即将传送或切换维度\n
        - cancel: bool 是否允许触发，默认为False，若设为True，可阻止触发后续的传送
        - entityId: str 实体的唯一ID
        - fromDimensionId: int 传送前所在的维度
        - toDimensionId: int 传送后的目标维度
        - fromX: int 传送前所在的x坐标
        - fromY: int 传送前所在的y坐标
        - fromZ: int 传送前所在的z坐标
        - toX: int 传送目标地点的x坐标
        - toY: int 传送目标地点的y坐标
        - toZ: int 传送目标地点的z坐标
        - cause: str 传送理由，详情见MinecraftEnum.EntityTeleportCause
        """

    def EntityChangeDimensionServerEvent(self, args):
        # type: (dict) -> None
        """
        实体维度改变时服务端抛出\n
        - entityId: str 实体id
        - fromDimensionId: int 维度改变前的维度
        - toDimensionId: int 维度改变后的维度
        - fromX: float 改变前的位置x
        - fromY: float 改变前的位置Y
        - fromZ: float 改变前的位置Z
        - toX: float 改变后的位置x
        - toY: float 改变后的位置Y
        - toZ: float 改变后的位置Z
        """

    def EntityDefinitionsEventServerEvent(self, args):
        # type: (dict) -> None
        """
        触发时机：生物定义json文件中设置的event触发时同时触发。生物行为变更事件\n
        - entityId: str 生物id
        - eventName: str 触发的事件名称
        """

    def ServerItemUseOnEvent(self, args):
        # type: (dict) -> None
        """
        玩家在对方块使用物品之前服务端抛出的事件。
        注：如果需要取消物品的使用需要同时在ClientItemUseOnEvent和ServerItemUseOnEvent中将ret设置为True才能正确取消。\n
        - entityId: str 玩家实体id
        - itemDict: dict 使用的物品的物品信息字典
        - x: int 方块 x 坐标值
        - y: int 方块 y 坐标值
        - z: int 方块 z 坐标值
        - blockName: str 方块的identifier
        - blockAuxValue: int 方块的附加值
        - face: int 点击方块的面，参考Facing枚举
        - dimensionId: int 维度id
        - clickX: float 点击点的x比例位置
        - clickY: float 点击点的y比例位置
        - clickZ: float 点击点的z比例位置
        - ret: bool 设为True可取消物品的使用
        """

    def DestroyBlockEvent(self, args):
        # type: (dict) -> None
        """
        触发时机：当方块已经被玩家破坏时触发该事件\n
        - x: int 方块x坐标
        - y: int 方块y坐标
        - z: int 方块z坐标
        - face: int 方块被敲击的面向id，参考Facing枚举
        - fullName: str 方块的identifier，包含命名空间及名称
        - auxData: int 方块附加值
        - playerId: str 破坏方块的玩家ID
        - dimensionId: int 维度id
        """

    def InventoryItemChangedServerEvent(self, args):
        # type: (dict) -> None
        """
        玩家背包物品变化时服务端抛出的事件\n
        - playerId: str  玩家实体id
        - slot: int  背包槽位
        - oldItemDict: dict  变化前槽位中的物品，格式参考物品信息字典
        - newItemDict: dict  变化后槽位中的物品，格式参考物品信息字典
        """

    def ClientLoadAddonsFinishServerEvent(self, args):
        # type: (dict) -> None
        """
        客户端mod加载完成时，服务端触发此事件\n
        加载顺序：mod原版UI -> 自定义UI\n
        - playerId: str 玩家id
        """

    def ServerChatEvent(self, args):
        # type: (dict) -> None
        """
        玩家发送聊天信息时触发\n
        - username: str 玩家名称
        - playerId: str 玩家id
        - message: str 玩家发送的聊天消息内容
        - cancel: bool 是否取消这个聊天事件，若取消可以设置为True
        - bChatById: bool 是否把聊天消息发送给指定在线玩家，而不是广播给所有在线玩家，若只发送某些玩家可以设置为True
        - bForbid: bool 是否禁言，仅apollo可用。true：被禁言，玩家聊天会提示“你已被管理员禁言”。
        - toPlayerIds: list 接收聊天消息的玩家id列表，bChatById为True时生效
        """

    def AddServerPlayerEvent(self, args):
        # type: (dict) -> None
        """
        触发时机：玩家加入时触发该事件。\n
        - id: str 玩家id\n
        - isTransfer: bool 是否是切服时进入服务器，仅用于Apollo。如果是True，则表示切服时加入服务器，若是False，则表示登录进入网络游戏\n
        - isReconnect: bool 是否是断线重连，仅用于Apollo。如果是True，则表示本次登录是断线重连，若是False，则表示本次是正常登录或者转服\n
        - isPeUser: bool 是否从手机端登录，仅用于Apollo。如果是True，则表示本次登录是从手机端登录，若是False，则表示本次登录是从PC端登录\n
        - transferParam: str 切服传入参数，仅用于Apollo。调用【TransferToOtherServer】或【TransferToOtherServerById】传入的切服参数\n
        - uid: int/long 仅用于Apollo，玩家的netease uid，玩家的唯一标识\n
        - proxyId: int 仅用于Apollo，当前客户端连接的proxy服务器id
        """

    def DelServerPlayerEvent(self, args):
        # type: (dict) -> None
        """
        删除玩家时触发该事件\n
        - id: str 玩家id
        - isTransfer: bool 是否是切服时退出服务器，仅用于Apollo。如果是True，则表示切服时退出服务器；若是False，则表示退出网络游戏
        - uid: int/long 玩家的netease uid，玩家的唯一标识
        """

    def AddEntityServerEvent(self, args):
        # type: (dict) -> None
        """
        服务端侧创建新实体，或实体从存档加载时触发\n
        - id: str 实体id
        - posX: float 位置x
        - posY: float 位置y
        - posZ: float 位置z
        - dimensionId: int 实体维度
        - isBaby: bool 是否为幼儿
        - engineTypeStr: str 实体类型
        - itemName: str 物品identifier（仅当物品实体时存在该字段）
        - auxValue: int 物品附加值（仅当物品实体时存在该字段）
        """

    def DamageEvent(self, args):
        # type: (dict) -> None
        """
        实体受到伤害时触发\n
        - srcId: str 伤害源id
        - projectileId: str 投射物id
        - entityId: str 被伤害id
        - damage: int 伤害值，允许修改，设置为0则此次造成的伤害为0
        - absorption: int 伤害吸收生命值，详见AttrType枚举的ABSORPTION
        - cause: str 伤害来源，详见Minecraft枚举值文档的ActorDamageCause
        - knock: bool 是否击退被攻击者，允许修改，设置该值为False则不产生击退
        - ignite: bool 是否点燃被伤害者，允许修改，设置该值为True产生点燃效果，反之亦然
        """

    def ActuallyHurtServerEvent(self, args):
        # type: (dict) -> None
        """
        实体实际受到伤害时触发，相比于DamageEvent，该伤害为经过护甲及buff计算后，实际的扣血量\n
        - srcId: str 伤害源id
        - projectileId: str 投射物id
        - entityId: str 被伤害id
        - damage: int 伤害值，允许修改，设置为0则此次造成的伤害为0
        - cause: str 伤害来源，详见Minecraft枚举值文档的ActorDamageCause
        """

    def EntityRemoveEvent(self, args):
        # type: (dict) -> None
        """
        实体被删除时触发\n
        - id: str 实体id\n
        """

    def MobDieEvent(self, args):
        # type: (dict) -> None
        """
        实体被玩家杀死时触发\n
        - id: str 实体id\n
        - attacker: str 伤害来源id
        """

    def PlayerAttackEntityEvent(self, args):
        # type: (dict) -> None
        """
        触发时机：当玩家攻击时触发该事件。\n
        - playerId: str 玩家id\n
        - victimId: str 受击者id\n
        - damage: int 伤害值：引擎传过来的值是0 允许脚本层修改为其他数\n
        - isValid: int 脚本是否设置伤害值：1表示是；0 表示否\n
        - cancel: bool 是否取消该次攻击，默认不取消\n
        - isKnockBack: bool 是否支持击退效果，默认支持，当不支持时将屏蔽武器击退附魔效果
        """

    def CommandEvent(self, args):
        # type: (dict) -> None
        """
        玩家请求执行指令时触发\n
        - entityId: str 玩家ID
        - command: str 指令字符串
        - cancel: bool 是否取消
        """

    def EntityPickupItemServerEvent(self, args):
        # type: (dict) -> None
        """
        有minecraft:behavior.pickup_items行为的生物拾取物品时触发该事件\n
        例如村民拾取面包、猪灵拾取金锭\n
        - entityId: str 生物Id\n
        - itemDict: dict 拾取的物品的物品信息字典\n
        - secondaryActor: str 物品给予者id（一般是玩家），如果不存在给予者的话，这里为空字符串
        """

    def ServerPlayerTryTouchEvent(self, args):
        # type: (dict) -> None
        """
        玩家即将捡起物品时触发\n
        - playerId: str 玩家Id\n
        - entityId: str 物品实体的Id\n
        - itemDict: dict 触碰的物品的物品信息字典\n
        - cancel: bool 设置为True时将取消本次拾取\n
        - pickupDelay: int 取消拾取后重新设置该物品的拾取cd，小于15帧将视作15帧，大于等于97813帧将视作无法拾取
        """

    def PlayerDieEvent(self, args):
        # type: (dict) -> None
        """
        触发时机：当玩家死亡时触发该事件\n
        - id: str 玩家id
        - attacker: str 伤害来源id
        """

    def PlayerEatFoodServerEvent(self, args):
        # type: (dict) -> None
        """
        触发时机：玩家吃下食物时触发\n
        - playerId: str 玩家Id
        - itemDict: dict 食物物品的物品信息字典
        - hunger: int 食物增加的饥饿值，可修改
        - nutrition: float 食物的营养价值，回复饱和度 = 食物增加的饥饿值 * 食物的营养价值 * 2，饱和度最大不超过当前饥饿值，可修改
        """

    def PlayerRespawnFinishServerEvent(self, args):
        # type: (dict) -> None
        """
        触发时机：玩家复活完毕时触发\n
        - playerId: str 玩家id
        """

    def ActorAcquiredItemServerEvent(self, args):
        # type: (dict) -> None
        """
        触发时机：玩家获得物品时服务端抛出的事件\n
        （有些获取物品方式只会触发客户端事件，有些获取物品方式只会触发服务端事件，在使用时注意一点。）\n
        - actor: str 获得物品玩家实体id
        - secondaryActor: str 物品给予者玩家实体id，如果不存在给予者的话，这里为空字符串
        - itemDict: dict 获得的物品的物品信息字典
        - acquireMethod: int 获得物品的方法，详见ItemAcquisitionMethod枚举
        """

    def PlayerIntendLeaveServerEvent(self, args):
        # type: (dict) -> None
        """
        触发时机：即将删除玩家时触发该事件，此时可以通过各种API获取玩家的当前状态。\n
        - playerId: str 玩家id
        """

    def ServerPlayerTryDestroyBlockEvent(self, args):
        # type: (dict) -> None
        """
        当玩家即将破坏方块时，服务端线程触发该事件\n
        - x: int 方块x坐标
        - y: int 方块y坐标
        - z: int 方块z坐标
        - face: int 方块被敲击的面向id，参考Facing枚举
        - fullName: str 方块的identifier，包含命名空间及名称
        - auxData: int 方块附加值
        - playerId: str 试图破坏方块的玩家ID
        - dimensionId: int 维度id
        - cancel: bool 默认为False，在脚本层设置为True就能取消该方块的破坏
        - spawnResources: bool 是否生成掉落物，默认为True，在脚本层设置为False就能取消生成掉落物
        """

    def EntityDieLoottableServerEvent(self, args):
        # type: (dict) -> None
        """
        触发时机：生物死亡掉落物品时\n
        只有当dirty为True时才会重新读取item列表并生成对应的掉落物，如果不需要修改掉落结果的话请勿随意修改dirty值\n
        - dieEntityId: str 死亡实体的entityId
        - attacker: str 伤害来源的entityId
        - itemList: list(dict) 掉落物品列表，每个元素为一个itemDict，格式可参考物品信息字典
        - dirty: bool 默认为False，如果需要修改掉落列表需将该值设为True
        """

    def ProjectileDoHitEffectEvent(self, args):
        # type: (dict) -> None
        """
        触发时机：当抛射物碰撞时触发该事件\n
        - id: str 子弹id
        - hitTargetType: str 碰撞目标类型,ENTITY或是BLOCK
        - targetId: str 碰撞目标id
        - hitFace: int 撞击在方块上的面id，参考Facing枚举
        - x: float 碰撞x坐标
        - y: float 碰撞y坐标
        - z: float 碰撞z坐标
        - blockPosX: int 碰撞是方块时，方块x坐标
        - blockPosY: int 碰撞是方块时，方块y坐标
        - blockPosZ: int 碰撞是方块时，方块z坐标
        - srcId: str 创建者id
        - cancel: bool 是否取消这个碰撞事件，若取消可以设置为True
        """

    def OnContainerFillLoottableServerEvent(self, args):
        # type: (dict) -> None
        """
        触发时机：随机奖励箱第一次打开根据loottable生成物品时\n
        只有当dirty为True时才会重新读取item列表并生成对应的掉落物，如果不需要修改掉落结果的话请勿随意修改dirty值\n
        - loottable: str 奖励箱子所读取的loottable的json路径
        - playerId: str 打开奖励箱子的玩家的playerId
        - itemList: list 掉落物品列表，每个元素为一个itemDict，格式可参考物品信息字典
        - dirty: bool 默认为False，如果需要修改掉落列表需将该值设为True
        """

    def PlaceNeteaseStructureFeatureEvent(self, args):
        # type: (dict) -> None
        """
        触发时机：首次生成地形时，结构特征即将生成时服务端抛出该事件。\n
        需要配合AddNeteaseFeatureWhiteList接口一同使用\n
        若在本监听事件中调用其他mod SDK接口将无法生效，强烈建议本事件仅用于设置结构放置与否\n
        - structureName: str 结构名称
        - x: int 结构坐标最小方块所在的x坐标
        - y: int 结构坐标最小方块所在的y坐标
        - z: int 结构坐标最小方块所在的z坐标
        - biomeType: int 该feature所放置区块的生物群系类型
        - biomeName: str 该feature所放置区块的生物群系名称
        - dimensionId: int 维度id
        - cancel: bool 设置为True时可阻止该结构的放置
        """

    def ServerSpawnMobEvent(self, args):
        # type: (dict) -> None
        """
        游戏内自动生成怪物时触发\n
        - identifier: str 生成实体的命名空间
        - type: int 生成实体的类型，参考EntityType
        - baby: bool 生成怪物是否是幼年怪
        - x: float 生成实体坐标x
        - y: float 生成实体坐标y
        - z: float 生成实体坐标z
        - dimensionId: int 生成实体的维度，默认值为0（0为主世界，1为地狱，2为末地）
        - realIdentifier: str 生成实体的命名空间，通过MOD API生成的生物在这个参数也能获取到真正的命名空间，而不是以custom开头的
        - cancel: bool 是否取消生成该实体
        """

    def DimensionChangeFinishServerEvent(self, args):
        # type: (dict) -> None
        """
        玩家维度改变完成后服务端抛出\n
        - playerId: str 玩家实体id
        - fromDimensionId: int 维度改变前的维度
        - toDimensionId: int 维度改变后的维度
        - toPos: tuple(float,float,float) 改变后的位置x,y,z,其中y值为脚底加上角色的身高值
        """

    def AddEffectServerEvent(self, args):
        # type: (dict) -> None
        """
        触发时机：实体获得状态效果时\n
        - entityId: str 实体id
        - effectName: str 实体获得状态效果的名字
        - effectDuration: int 状态效果的持续时间，单位秒
        - effectAmplifier: int 状态效果的放大倍数
        - damage: int 状态造成的伤害值，如药水
        """

    def RemoveEffectServerEvent(self, args):
        # type: (dict) -> None
        """
        触发时机：实体身上状态效果被移除时\n
        - entityId: str 实体id
        - effectName: str 被移除状态效果的名字
        - effectDuration: int 被移除状态效果的剩余持续时间，单位秒
        - effectAmplifier: int 被移除状态效果的放大倍数
        """

    def RefreshEffectServerEvent(self, args):
        # type: (dict) -> None
        """
        触发时机：实体身上状态效果更新时触发，更新条件:\n
        1、新增状态等级较高，更新状态等级及时间；\n
        2、新增状态等级不变，时间较长，更新状态持续时间\n
        - entityId: str 实体id
        - effectName: str 更新状态效果的名字
        - effectDuration: int 更新后状态效果剩余持续时间，单位秒
        - effectAmplifier: int 更新后的状态效果放大倍数
        - damage: int 状态造成的伤害值，如药水
        """

    def WillAddEffectServerEvent(self, args):
        # type: (dict) -> None
        """
        触发时机：实体即将获得状态效果前\n
        - entityId: str 实体id
        - effectName: str 实体获得状态效果的名字
        - effectDuration: int 状态效果的持续时间，单位秒
        - effectAmplifier: int 状态效果的放大倍数
        - cancel: bool 设置为True可以取消
        - damage: int 状态造成的伤害值，如药水；需要注意，该值不一定是最终的伤害值
        """

    def HealthChangeBeforeServerEvent(self, args):
        # type: (dict) -> None
        """
        生物生命值发生变化之前触发\n
        - entityId: str 实体id
        - from: float 变化前的生命值
        - to: float 将要变化到的生命值，cancel设置为True时可以取消该变化，但是此参数不变
        - byScript: bool 是否通过SetAttrValue或SetAttrMaxValue调用产生的变化
        - cancel: bool 是否取消该变化
        """

    def ServerEntityTryPlaceBlockEvent(self, args):
        # type: (dict) -> None
        """
        触发时机：当生物试图放置方块时触发该事件。\n
        - x: int 方块x坐标
        - y: int 方块y坐标
        - z: int 方块z坐标
        - fullName: str 方块的identifier，包含命名空间及名称
        - auxData: int 方块附加值
        - entityId: str 试图放置方块的生物ID
        - dimensionId: int 维度id
        - face: int 点击方块的面，参考Facing枚举
        - cancel: bool 默认为False，在脚本层设置为True就能取消该方块的放置
        """

    def PistonActionServerEvent(self, args):
        # type: (dict) -> None
        """
        触发时机：活塞或者粘性活塞推送/缩回影响附近方块时\n
        - cancel: bool 是否允许触发，默认为False，若设为True，可阻止触发后续的事件
        - action: str 推送时=expanding；缩回时=retracting
        - pistonFacing: int 活塞的朝向，参考Facing枚举
        - pistonMoveFacing: int 活塞的运动方向，参考Facing枚举
        - dimensionId: int 活塞方块所在的维度
        - pistonX: int 活塞方块的x坐标
        - pistonY: int 活塞方块的y坐标
        - pistonZ: int 活塞方块的z坐标
        - blockList: list[(x,y,z),...] 活塞运动影响到产生被移动效果的方块坐标(x,y,z)，均为int类型
        - breakBlockList: list[(x,y,z),...] 活塞运动影响到产生被破坏效果的方块坐标(x,y,z)，均为int类型
        - entityList: list[string,...] 活塞运动影响到产生被移动或被破坏效果的实体的ID列表
        """


class ClientDefaultEvent(object):
    """客户端原版事件"""
    GridComponentSizeChangedClientEvent = "GridComponentSizeChangedClientEvent"
    DimensionChangeClientEvent = "DimensionChangeClientEvent"
    OnLocalPlayerStopLoading = "OnLocalPlayerStopLoading"
    LoadClientAddonScriptsAfter = "LoadClientAddonScriptsAfter"
    AddPlayerCreatedClientEvent = "AddPlayerCreatedClientEvent"
    ClientChestOpenEvent = "ClientChestOpenEvent"
    ClientChestCloseEvent = "ClientChestCloseEvent"
    ClientBlockUseEvent = "ClientBlockUseEvent"
    OnGroundClientEvent = "OnGroundClientEvent"
    OnClientPlayerStartMove = "OnClientPlayerStartMove"
    AddEntityClientEvent = "AddEntityClientEvent"
    AddExpEvent = "AddExpEvent"
    AddLevelEvent = "AddLevelEvent"
    UiInitFinished = "UiInitFinished"
    OnKeyPressInGame = "OnKeyPressInGame"
    TapBeforeClientEvent = "TapBeforeClientEvent"
    LeftClickBeforeClientEvent = "LeftClickBeforeClientEvent"
    LeftClickReleaseClientEvent = "LeftClickReleaseClientEvent"
    RightClickBeforeClientEvent = "RightClickBeforeClientEvent"
    RightClickReleaseClientEvent = "RightClickReleaseClientEvent"
    HoldBeforeClientEvent = "HoldBeforeClientEvent"
    GetEntityByCoordReleaseClientEvent = "GetEntityByCoordReleaseClientEvent"
    ClientJumpButtonPressDownEvent = "ClientJumpButtonPressDownEvent"
    OnCarriedNewItemChangedClientEvent = "OnCarriedNewItemChangedClientEvent"
    RemoveEntityClientEvent = "RemoveEntityClientEvent"
    OnScriptTickClient = "OnScriptTickClient"
    GetEntityByCoordEvent = "GetEntityByCoordEvent"
    ServerPlayerGetExperienceOrbEvent = "ServerPlayerGetExperienceOrbEvent"
    ClientPlayerInventoryOpenEvent = "ClientPlayerInventoryOpenEvent"
    OnItemSlotButtonClickedEvent = "OnItemSlotButtonClickedEvent"
    InventoryItemChangedClientEvent = "InventoryItemChangedClientEvent"
    DimensionChangeFinishClientEvent = "DimensionChangeFinishClientEvent"
    PerspChangeClientEvent = "PerspChangeClientEvent"
    ApproachEntityClientEvent = "ApproachEntityClientEvent"
    AddPlayerAOIClientEvent = "AddPlayerAOIClientEvent"
    RemovePlayerAOIClientEvent = "RemovePlayerAOIClientEvent"
    LeaveEntityClientEvent = "LeaveEntityClientEvent"
    GameTypeChangedClientEvent = "GameTypeChangedClientEvent"
    UnLoadClientAddonScriptsBefore = "UnLoadClientAddonScriptsBefore"
    ScreenSizeChangedClientEvent = "ScreenSizeChangedClientEvent"
    ClientJumpButtonReleaseEvent = "ClientJumpButtonReleaseEvent"
    MouseWheelClientEvent = "MouseWheelClientEvent"
    OnMouseMiddleDownClientEvent = "OnMouseMiddleDownClientEvent"


class ClientEvent(modConfig.ModClient, ClientDefaultEvent):
    """客户端事件"""
    # 模块事件
    ClientModuleFinishedLoadEvent = "ClientModuleFinishedLoadEvent"  # 客户端模块加载完成事件
    OnPlayerOpenChestEvent = "OnPlayerOpenChestEvent"  # 客户端打开箱子事件
    RequestExecuteCommandEvent = "RequestExecuteCommandEvent"  # 请求执行指令事件
    ResponseLoadModConfigEvent = "ResponseLoadModConfigEvent"  # 响应导入配置文件事件


class ClientRecall(object):
    """客户端回调"""

    def GridComponentSizeChangedClientEvent(self, args):
        # type: (dict) -> None
        """触发时机：UI grid组件里格子数目发生变化时触发"""

    def DimensionChangeClientEvent(self, args):
        # type: (dict) -> None
        """
        玩家维度改变时客户端抛出\n
        - playerId: str 玩家实体id
        - fromDimensionId: int 维度改变前的维度
        - toDimensionId: int 维度改变后的维度
        - fromX: float 改变前的位置x
        - fromY: float 改变前的位置Y
        - fromZ: float 改变前的位置Z
        - toX: float 改变后的位置x
        - toY: float 改变后的位置Y
        - toZ: float 改变后的位置Z
        """

    def OnMouseMiddleDownClientEvent(self, args):
        # type: (dict) -> None
        """
        鼠标按下中键时触发\n
        - isDown: int 1为按下，0为弹起
        - mousePositionX: float 按下时的x坐标
        - mousePositionY: float 按下时的y坐标
        """

    def MouseWheelClientEvent(self, args):
        # type: (dict) -> None
        """
        鼠标滚轮滚动时触发\n
        - direction: int 1为向上滚动，0为向下滚动
        """

    def ClientJumpButtonReleaseEvent(self, args):
        # type: (dict) -> None
        """跳跃按钮按下释放事件"""

    def ScreenSizeChangedClientEvent(self, args):
        # type: (dict) -> None
        """
        改变屏幕大小时会触发的事件\n
        - 仅PC端有效
        - beforeX: float 屏幕大小改变前的宽度
        - beforeY: float 屏幕大小改变前的高度
        - afterX: float 屏幕大小改变后的宽度
        - afterY: float 屏幕大小改变后的高度
        """

    def UnLoadClientAddonScriptsBefore(self, args):
        # type: (dict) -> None
        """客户端卸载mod之前触发"""

    def OnLocalPlayerStopLoading(self, args):
        # type: (dict) -> None
        """
        触发时机：玩家进入存档，出生点地形加载完成时触发。该事件触发时可以进行切换维度的操作。\n
        - playerId: str 加载完成的玩家id
        """

    def GameTypeChangedClientEvent(self, args):
        # type: (dict) -> None
        """
        个人游戏模式发生变化时客户端触发。\n
        - playerId: str 玩家Id
        - oldGameType: int 切换前的游戏模式
        - newGameType: int 切换后的游戏模式
        """

    def LoadClientAddonScriptsAfter(self, args):
        # type: (dict) -> None
        """客户端加载mod完成事件"""

    def AddPlayerCreatedClientEvent(self, args):
        # type: (dict) -> None
        """
        玩家进入当前玩家所在的区块AOI后，玩家皮肤数据异步加载完成后触发的事件\n
        由于玩家皮肤是异步加载的原因，该事件触发时机比AddPlayerAOIClientEvent晚，触发该事件后可以对该玩家调用相关玩家渲染接口。\n
        当前客户端每加载好一个玩家的皮肤，就会触发一次该事件，比如刚进入世界时，localPlayer加载好会触发一次，周围的所有玩家加载好后也会分别触发一次。\n
        - playerId: str 玩家id
        """

    def ClientChestOpenEvent(self, args):
        # type: (dict) -> None
        """
        打开箱子界面时触发，包括小箱子，合并后大箱子和末影龙箱子\n
        - playerId: str 玩家实体id
        - x: int 箱子位置x值
        - y: int 箱子位置y值
        - z: int 箱子位置z值
        """

    def ClientChestCloseEvent(self, _):
        # type: (dict) -> None
        """关闭箱子界面时触发，包括小箱子，合并后大箱子和末影龙箱子"""

    def OnScriptTickClient(self):
        """客户端tick事件,1秒30次"""

    def GetEntityByCoordReleaseClientEvent(self, args):
        """
        玩家点击屏幕后松开时触发，多个手指点在屏幕上时，只有最后一个手指松开时触发。\n
        - x: int 屏幕坐标x
        - y: int 屏幕坐标y
        """

    def ClientBlockUseEvent(self, args):
        # type: (dict) -> None
        """
        触发时机：玩家右键点击新版自定义方块\n
        时客户端抛出该事件（该事件tick执行，需要注意效率问题）。\n
        - playerId: str 玩家Id
        - blockName: str 方块的identifier，包含命名空间及名称
        - aux: int 方块附加值
        - cancel: bool 设置为True可拦截与方块交互的逻辑。
        - x: int 方块x坐标
        - y: int 方块y坐标
        - z: int 方块z坐标
        """

    def LeftClickBeforeClientEvent(self, args):
        # type: (dict) -> None
        """
        玩家按下鼠标左键时触发。仅在pc的普通控制模式（即非F11模式）下触发。\n
        - cancel: bool - 设置为True可拦截原版的挖方块或攻击响应
        """

    def LeftClickReleaseClientEvent(self, _):
        """
        玩家松开鼠标左键时触发。\n
        仅在pc的普通控制模式（即非F11模式）下触发。
        """

    def RightClickBeforeClientEvent(self, args):
        # type: (dict) -> None
        """
        玩家按下鼠标右键时触发。仅在pc下触发（普通控制模式及F11模式都会触发）\n
        - cancel: bool - 设置为True可拦截原版的物品使用/实体交互响应
        """

    def RightClickReleaseClientEvent(self, _):
        """
        玩家松开鼠标右键时触发。\n
        仅在pc的普通控制模式（即非F11模式）下触发。\n
        - 在F11下右键，按下会触发RightClickBeforeClientEvent
        - 松开时会触发TapOrHoldReleaseClientEvent
        """

    def OnGroundClientEvent(self, args):
        # type: (dict) -> None
        """
        实体着地事件。玩家，沙子，铁砧，掉落的物品，点燃的TNT掉落地面时触发，其余实体着地不触发。\n
        - id: str 实体id
        """

    def ClientJumpButtonPressDownEvent(self, args):
        # type: (dict) -> None
        """
        跳跃按钮按下事件，返回值设置参数只对当次按下事件起作用\n
        - continueJump: bool 设置是否执行跳跃逻辑
        """

    def OnClientPlayerStartMove(self):
        """移动按钮按下触发事件，在按住一个方向键的同时，去按另外一个方向键，不会触发第二次"""

    def AddEntityClientEvent(self, args):
        # type: (dict) -> None
        """
        客户端侧创建新实体时触发\n
        - id: str 实体id
        - posX: float 位置x
        - posY: float 位置y
        - posZ: float 位置z
        - dimensionId: int 实体维度
        - isBaby: bool 是否为幼儿
        - engineTypeStr: str 实体类型
        - itemName: str 物品identifier（仅当物品实体时存在该字段）
        - auxValue: int 物品附加值（仅当物品实体时存在该字段）
        """

    def UiInitFinished(self, args):
        # type: (dict) -> None
        """
        客户端UI初始化完成事件\n
        - 切换维度时会重新加载UI
        """

    def OnKeyPressInGame(self, args):
        # type: (dict) -> tuple
        """
        键盘按键触发事件\n
        - screenName: str - 当前screenName
        - isDown: str - 0抬起 1按下
        - key: str - 按键值，需使用keyType检测
        """
        return args["screenName"], args["isDown"] == "1", int(args["key"])

    def TapBeforeClientEvent(self, args):
        # type: (dict) -> None
        """
        玩家点击屏幕并松手，即将响应到游戏内时触发。仅在移动端或pc的F11模式下触发。\n
        pc的非F11模式可以使用LeftClickBeforeClientEvent事件监听鼠标左键\n
        - cancel: bool - 设置为True可拦截原版的攻击或放置响应
        """

    def RemoveEntityClientEvent(self, args):
        # type: (dict) -> None
        """
        客户端侧实体被移除时触发\n
        - id: str - 移除的实体id
        """

    def HoldBeforeClientEvent(self, args):
        # type: (dict) -> None
        """
        玩家长按屏幕，即将响应到游戏内时触发。仅在移动端或pc的F11模式下触发。\n
        pc的非F11模式可以使用RightClickBeforeClientEvent事件监听鼠标右键\n
        - cancel: bool - 设置为True可拦截原版的挖方块/使用物品/与实体交互响应
        """

    def GetEntityByCoordEvent(self, args):
        # type: (dict) -> None
        """玩家点击屏幕时触发，多个手指点在屏幕上时，只有第一个会触发"""

    def AddExpEvent(self, args):
        # type: (dict) -> None
        """
        触发时机：当玩家增加经验时触发该事件。\n
        - id: str 玩家id
        - addExp: int 增加的经验值
        """

    def AddLevelEvent(self, args):
        # type: (dict) -> None
        """
        触发时机：当玩家升级时触发该事件。\n
        - id: str 玩家id
        - addLevel: int 增加的等级值
        - newLevel: int 新的等级
        """

    def ServerPlayerGetExperienceOrbEvent(self, args):
        # type: (dict) -> None
        """
        触发时机：玩家获取经验球时触发的事件\n
        - playerId: str 玩家id
        - experienceValue: int 经验球经验值
        - cancel: bool 是否取消（开发者传入）
        """

    def ClientPlayerInventoryOpenEvent(self, args):
        """
        打开物品背包界面时触发\n
        - isCreative: bool 是否是创造模式背包界面
        - cancel: bool 取消打开物品背包界面
        """

    def OnItemSlotButtonClickedEvent(self, args):
        # type: (dict) -> None
        """
        点击快捷栏和背包栏的物品槽时触发\n
        - slotIndex: int 点击的物品槽的编号
        """

    def InventoryItemChangedClientEvent(self, args):
        # type: (dict) -> None
        """
        玩家背包物品变化时客户端抛出的事件。\n
        - playerId: str 玩家实体id
        - slot: int 背包槽位
        - oldItemDict: dict 变化前槽位中的物品，格式参考物品信息字典
        - newItemDict: dict 变化后槽位中的物品，格式参考物品信息字典
        """

    def DimensionChangeFinishClientEvent(self, args):
        # type: (dict) -> None
        """
        玩家维度改变完成后客户端抛出\n
        - playerId str 玩家实体id
        - fromDimensionId int 维度改变前的维度
        - toDimensionId int 维度改变后的维度
        - toPos tuple(float,float,float) 改变后的位置x,y,z,其中y值为脚底加上角色的身高值
        """

    def PerspChangeClientEvent(self, args):
        # type: (dict) -> None
        """
        视角切换时会触发的事件\n
        - from: int 切换前的视角
        - to: int 切换后的视角
        """

    def ApproachEntityClientEvent(self, args):
        # type: (dict) -> None
        """
        玩家靠近生物时触发\n
        - playerId: str 玩家实体id
        - entityId: str 靠近的生物实体id
        """

    def AddPlayerAOIClientEvent(self, args):
        # type: (dict) -> None
        """
        玩家加入游戏或者其余玩家进入当前玩家所在的区块时触发的AOI事件，替换AddPlayerEvent\n
        - playerId: str 玩家id
        """

    def RemovePlayerAOIClientEvent(self, args):
        # type: (dict) -> None
        """
        玩家离开当前玩家同一个区块时触发AOI事件\n
        - playerId: str 玩家id
        """

    def OnCarriedNewItemChangedClientEvent(self, args):
        # type: (dict) -> None
        """
        OnCarriedNewItemChangedClientEvent\n
        - itemDict: dict 切换后物品的物品信息字典
        """


class UIEvent(modConfig.ModUI):
    """UI事件"""
    OnUIExitBlockScreenEvent = "OnUIExitBlockScreenEvent"
    OnUIOpenBlockScreenEvent = "OnUIOpenBlockScreenEvent"
    UIRequestChangeBlockStateEvent = "UIRequestChangeBlockStateEvent"
    # -----------------------------------------------------------------------------------
    UIRequestChangeDimensionEvent = "UIRequestChangeDimensionEvent"  # 请求传送模组维度事件
    OnUIScreenFinishedCreateEvent = "OnUIScreenFinishedCreateEvent"  # UI完成创建事件
    UIRequestPickEntityData = "UIRequestPickEntityData"  # UI请求准心选中生物数据
    OnUINodeDestroyEvent = "OnUINodeDestroyEvent"  # UI销毁事件
    # -----------------------------------------------------------------------------------
    UIRequestSwitchInvItems = "UIRequestSwitchInvItems"  # 请求同步背包物品事件
    UIRequestExchangeItemsWithBlock = "UIRequestExchangeItemsWithBlock"  # 玩家与方块物品交换
    UIRequestBlockSwitchItemsEvent = "UIRequestBlockSwitchItemsEvent"  # 方块之间物品交换
    UIRequestUpgradeBlockEvent = "UIRequestUpgradeBlockEvent"  # 玩家请求方块升级事件
