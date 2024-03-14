# -*- coding:utf-8 -*-


import mod.server.extraServerApi as serverApi


class ServerStructure(object):
    """结构服务端"""

    @classmethod
    def PlaceStructure(cls, pos, name, dim, rot=0):
        # type: (tuple, str, int, int) -> bool
        """
        放置结构\n
        放置时需要确保所放置的区块都已加载，否则会放置失败或者部分缺失\n
        该接口是同步执行的，请勿在一帧内放置大量结构，会造成游戏卡顿\n
        - pos: tuple(float,float,float) 放置结构的位置
        - structureName: str 结构名称
        - dimensionId: int 希望放置结构的维度，可在对应维度的常加载区块放置结构，默认为-1
        - rotation: int 放置结构的旋转角度，默认为0(只可旋转90，180，270度)
        """
        game_comp = serverApi.GetEngineCompFactory().CreateGame(serverApi.GetLevelId())
        return game_comp.PlaceStructure(None, pos, name, dim, rot)
