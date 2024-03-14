# -*- coding:utf-8 -*-


import mod.server.extraServerApi as serverApi


class LobbyCloud(object):
    """云端大厅接口"""

    def __init__(self):
        comp_factory = serverApi.GetEngineCompFactory()
        self.http_comp = comp_factory.CreateHttp(serverApi.GetLevelId())

    def GetUid(self, player_id):
        # type: (str) -> int
        """
        获取玩家的uid。只有在线玩家才可获取\n
        - playerId: str 玩家实体id
        """
        return self.http_comp.GetPlayerUid(player_id)

    def LobbyGetStorage(self, callback, uid, key, *args):
        """
        获取存储的数据。仅联机大厅可用\n
        - callback: function 请求回调函数
        - uid: int 玩家uid，如果传0表示获取全局数据
        - keys: list(str) 查询数据的key列表，排序key与非排序key都可获取
        """
        self.http_comp.LobbyGetStorage(callback, uid, key)

    def LobbyGetStorageBySort(self, callback, key, ascend, offset, length, *args):
        """
        排序获取存储的数据。仅联机大厅可用\n
        - callback: function 请求回调函数
        - key: str 查询数据的key。在开发者平台上配置的可排序的key才可以查询
        - ascend: bool 是否升序
        - offset: int 从排序后的第几个数据开始返回（从0开始计算）
        - length: int 返回多少个数据，上限为50
        """
        self.http_comp.LobbyGetStorageBySort(callback, key, ascend, offset, length)

    def LobbySetStorageAndUserItem(self, callback, uid, order_id, entities_getter, *args):
        """
        设置订单已发货或者存数据。仅联机大厅可用\n
        - callback: function 请求回调函数
        - uid: int 玩家uid，如果传0表示设置全局数据
        - orderId: int或None 订单Id，可选
        - entitiesGetter: function或None 用于返回存储的数据的函数，可选
        """
        self.http_comp.LobbySetStorageAndUserItem(callback, uid, order_id, entities_getter)

    def QueryLobbyUserItem(self, callback, uid, *args):
        """
        查询还没发货的订单。仅联机大厅可用\n
        - callback: function 请求回调函数
        - uid: int 玩家uid
        """
        self.http_comp.QueryLobbyUserItem(callback, uid)
