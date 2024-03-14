# -*- coding:utf-8 -*-


import random

from const import *
from ..system.preset import LoadConfigModuleServer
from ...common.system.base import *
from ...server.entity import *
from ...server.item import ServerItem


class LootModuleServer(LoadConfigModuleServer):
    """战利品模块服务端"""
    __mVersion__ = 10
    __identifier__ = ModuleEnum.identifier
    _ModuleRequestRegisterEvent = ModuleEvent.ModuleRequestLootRegisterEvent

    def __init__(self):
        super(LootModuleServer, self).__init__()
        level_id = serverApi.GetLevelId()
        self.block_comp = self.comp_factory.CreateBlockInfo(level_id)
        self.item_comp = self.comp_factory.CreateItem(level_id)

    def ConfigEvent(self):
        super(LootModuleServer, self).ConfigEvent()
        self.defaultEvent.update({
            ServerEvent.PlayerEatFoodServerEvent: (self.PlayerEatFoodServerEvent, 5),
            ServerEvent.ServerPlayerTryDestroyBlockEvent: (self.ServerPlayerTryDestroyBlockEvent, 5),
            ServerEvent.ServerEntityTryPlaceBlockEvent: (self.ServerEntityTryPlaceBlockEvent, 5),
            ServerEvent.EntityDieLoottableServerEvent: self.EntityDieLoottableServerEvent,
        })
        self.clientEvent.update({
            ClientEvent.OnPlayerOpenChestEvent: (self.OnPlayerOpenChestEvent, 5)
        })

    # -----------------------------------------------------------------------------------

    def EntityDieLoottableServerEvent(self, args):
        entity_id = args["dieEntityId"]
        engine_type = RawEntity.GetTypeStr(entity_id)

        # 需要生成到列表内
        # args["dirty"] = True

    def PlayerEatFoodServerEvent(self, args):
        playerId = args["playerId"]
        itemDict = args["itemDict"]  # type: dict
        itemName = itemDict["newItemName"]
        config = ModuleLootEnum.GetConfig(itemName)
        if not config:
            return
        pos = RawEntity.GetPos(playerId)
        dim = RawEntity.GetDim(playerId)
        for item in ModuleParser.GetSelf().Parse(config):
            self.item_comp.SpawnItemToLevel(item, dim, pos)

    def OnPlayerOpenChestEvent(self, args):
        """
        玩家开启箱子事件\n
        - playerId: str
        - dim: int
        - pos: tuple
        """
        # playerId = args["playerId"]
        pos = args["pos"]
        dim = args["dim"]

        itemDict = self.item_comp.GetContainerItem(pos, 0, dim, True)
        if not isinstance(itemDict, dict):
            return
        itemName = itemDict["newItemName"]
        if not itemName == GameBlock.barrier:
            return
        if not self.ActiveLoot(itemDict, pos, dim):
            return

    def ServerPlayerTryDestroyBlockEvent(self, args):
        player_id = args["playerId"]
        block_name = args["fullName"]
        if block_name != GameBlock.chest:
            return
        spawn_dim = args["dimensionId"]
        spawn_pos = (args["x"], args["y"], args["z"])
        item = self.item_comp.GetContainerItem(spawn_pos, 0, spawn_dim, True)
        if not isinstance(item, dict):
            return
        if item["newItemName"] != GameBlock.barrier:
            return
        if not self.ActiveLoot(item, spawn_pos, spawn_dim):
            return
        args["spawnResources"] = False

    def ServerEntityTryPlaceBlockEvent(self, args):
        entity_id = args["entityId"]
        block_pos = (args["x"], args["y"], args["z"])
        block_dim = args["dimensionId"]
        block_name = args["fullName"]
        if block_name not in GameTag.Container:
            return
        entity = LivingEntity(entity_id)
        selected_item = entity.GetSelectedItem()
        data = ServerItem.GetExtraId(selected_item)
        if "loot" not in data:
            return
        config = data["loot"]
        loot_type, name = config["type"], config["name"]
        items = []
        if loot_type == "entity":
            lootComp = self.comp_factory.CreateActorLoot(entity_id)
            if not lootComp.SpawnLootTable(block_pos, name):
                return
            for itemId in self.GetSquareEntities(block_pos, block_dim, radius=1):
                if not RawEntity.IsItem(itemId):
                    continue
                itemDict = self.item_comp.GetDroppedItem(itemId, True)
                items.append(itemDict)
                self.system.DestroyEntity(itemId)

        def active():
            for _ in xrange(10):
                yield 1
                block_info = self.block_comp.GetBlockNew(block_pos, block_dim)
                slots = random.sample([x for x in xrange(36)], len(items))
                if block_info["name"] != block_name:
                    continue
                if items:
                    for index, item in enumerate(items):
                        slot = slots[index]
                        self.item_comp.SpawnItemToContainer(item, slot, block_pos, block_dim)
                else:
                    marker = self.Item.Create(GameBlock.barrier, extraId={"loot": name})
                    self.item_comp.SpawnItemToContainer(marker, 0, block_pos, block_dim)
                return

        self.StartCoroutine(active)

    # -----------------------------------------------------------------------------------

    @classmethod
    def GetLootParser(cls):
        # type: () -> ModuleParser
        """获得战利品解释器"""
        return ModuleParser.GetSelf()

    @classmethod
    def ParseLootConfig(cls, config_id):
        # type: (str) -> list
        """解析战利品配置"""
        config = ModuleLootEnum.GetConfig(config_id)  # type: dict
        if not config:
            print "[warn]", "Invalid config id: %s" % config_id
            return []
        return ModuleParser.GetSelf().Parse(config)

    def ActiveLoot(self, item, pos, dim):
        # type: (dict, tuple, int) -> bool
        """生成战利品"""
        data = ServerItem.GetExtraId(item)
        loot = data.get("loot")  # type: str
        if not loot:
            loot = ServerItem.GetCustomName(item)
            if not loot:
                loot = "default"
        config = ModuleLootEnum.GetConfig(loot)  # type: list
        if not config:
            print "[info]", "Invalid loot: %s" % loot
            return False
        self.item_comp.SpawnItemToContainer({"name": GameBlock.air, "aux": 0}, 0, pos, dim)
        # -----------------------------------------------------------------------------------
        items = ModuleParser.GetSelf().Parse(config)
        slots = random.sample([x for x in xrange(27)], len(items))
        for index, item in enumerate(items):
            slot = slots[index]
            self.item_comp.SpawnItemToContainer(item, slot, pos, dim)
        return True

    def OnLoadModConfig(self, data):
        ModuleLootEnum.LootConfig = data
        return True
