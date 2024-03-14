# -*- coding:utf-8 -*-


import mod.server.extraServerApi as serverApi
from ..parts.base import ConditionBase


# 方块状态属性检测条件
class BlockStatePropertyCondition(ConditionBase):
    """方块状态属性检测条件"""
    __mVersion__ = 1

    def Parse(self):
        block = self.data["block"]  # type: str
        properties = self.data.get("properties")

        block_comp = self.comp_factory.CreateBlockInfo(serverApi.GetLevelId())
        block_name = block_comp.GetBlockNew(self.predicate_pos, self.predicate_dim)["name"]
        return block_name == block
