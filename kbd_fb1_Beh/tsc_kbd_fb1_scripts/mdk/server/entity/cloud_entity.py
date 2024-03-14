# -*- coding:utf-8 -*-


from player_entity import PlayerEntity
from ..cloud.lobby import LobbyCloud


class CloudPlayerEntity(PlayerEntity, LobbyCloud):
    """云端玩家类"""
    __mVersion__ = 1

    def __init__(self, playerId):
        super(CloudPlayerEntity, self).__init__(playerId)
        self.uid = self.GetUid(self.id)

    def LobbyGetStorage(self, callback, key, *args):
        super(CloudPlayerEntity, self).LobbyGetStorage(callback, self.uid, key)

    def LobbyGetStorageBySort(self, callback, key, ascend, offset, length, *args):
        super(CloudPlayerEntity, self).LobbyGetStorageBySort(callback, key, ascend, offset, length)

    def LobbySetStorageAndUserItem(self, callback, order_id, entities_getter, *args):
        super(CloudPlayerEntity, self).LobbySetStorageAndUserItem(callback, self.uid, order_id, entities_getter)

    def QueryLobbyUserItem(self, callback, *args):
        super(CloudPlayerEntity, self).QueryLobbyUserItem(callback, self.uid)
