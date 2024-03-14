# -*- coding:utf-8 -*-


import mod.server.extraServerApi as serverApi

from ..parts.base import PredicateBase


# 位置断言
class LocationPredicate(PredicateBase):
    """位置断言"""
    __mVersion__ = 1

    def __init__(self, check_pos, data, context):
        super(LocationPredicate, self).__init__(data, context)
        self.game_comp = self.comp_factory.CreateGame(serverApi.GetLevelId())
        self.check_pos = (int(check_pos[0]), int(check_pos[1]), int(check_pos[2]))
        block_comp = self.comp_factory.CreateBlockInfo(serverApi.GetLevelId())
        self.block_info = block_comp.GetBlockNew(self.check_pos, self.predicate_dim)

    def Parse(self):
        # 方块信息
        key = "block"
        if key in self.data:
            data = self.data[key]
            if not self.TestBlock(data):
                return False
        # 位置信息
        key = "position"
        if key in self.data:
            data = self.data[key]
            if not self.TestPosition(data):
                return False
        # 群系信息
        key = "biome"
        if key in self.data:
            data = self.data[key]
            if not self.TestBiome(data):
                return False
        # 测试维度信息
        key = "dimension"
        if key in self.data:
            data = self.data[key]
            if not self.TestDimension(data):
                return False
        # 测试光源强度信息
        key = "light"
        if key in self.data:
            data = self.data[key]
            if not self.TestLight(data):
                return False

    # -----------------------------------------------------------------------------------

    def TestBlock(self, data):
        # type: (dict) -> bool
        """测试方块信息"""
        # 检测方块名称
        key = "blocks"
        if key in data:
            value = data[key]  # type: list
            block_name = self.block_info["name"]
            if block_name not in value:
                return False

        key = "tag"
        key = "nbt"

    def TestPosition(self, data):
        # type: (dict) -> bool
        """测试位置信息"""
        for index, key in enumerate(["x", "y", "z"]):
            if key not in data:
                continue
            value = self.check_pos[index]
            target = data[key]
            if not self.TestValue(value, target):
                return False

    def TestBiome(self, data):
        # type: (str) -> bool
        """测试群系信息"""
        biome_comp = self.comp_factory.CreateBiome(serverApi.GetLevelId())
        return biome_comp.GetBiomeName(self.check_pos, self.predicate_dim) == data

    def TestDimension(self, data):
        # type: (any) -> bool
        """测试维度信息"""
        return self.TestValue(self.predicate_dim, data)

    def TestLight(self, data):
        # type: (any) -> bool
        """测试光照信息"""
