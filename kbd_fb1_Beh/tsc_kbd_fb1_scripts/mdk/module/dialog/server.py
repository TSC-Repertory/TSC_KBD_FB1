# -*- coding:utf-8 -*-


from const import *
from parts.entity import DialogEntity
from ..system.preset import *


class DialogModuleServer(LoadConfigModuleServer):
    """对话模块服务端"""
    __mVersion__ = 2
    __identifier__ = ModuleEnum.identifier
    _ModuleRequestRegisterEvent = ModuleEvent.ModuleRequestDialogRegisterEvent

    def __init__(self):
        super(DialogModuleServer, self).__init__()
        self._dirty_player = set()

    def OnDestroy(self):
        del self._dirty_player
        super(DialogModuleServer, self).OnDestroy()

    def ConfigEvent(self):
        super(DialogModuleServer, self).ConfigEvent()
        self.clientEvent.update({
            ClientEvent.OnKeyPressInGame: self.OnKeyPressInGame
        })

        # -----------------------------------------------------------------------------------

    def GetDefaultConfig(self):
        return ["dialogs/root.json"]

    def CreateDialog(self, entityId, dialogId, context):
        # type: (str, str, dict) -> bool
        """创建对话"""
        config = ModuleDialog.GetData(dialogId)  # type: dict
        if not config or "type" not in config:
            print "[warn]", "Invalid dialog id: %s" % dialogId
            return False
        DialogEntity(entityId).ParseDialog(config)(context)
        return True

    # -----------------------------------------------------------------------------------

    def OnLoadModConfig(self, data):
        ModuleDialog.DialogData = data
        for playerId in self._dirty_player:
            self.NotifyToClient(playerId, ModuleEvent.ModuleRequestSynDialogDataEvent, {
                "data": ModuleDialog.DialogData
            })
        self._dirty_player.clear()
        return True

    # -----------------------------------------------------------------------------------

    def ClientLoadAddonsFinishServerEvent(self, args):
        playerId = args["playerId"]
        if not self._load_data:
            self._dirty_player.add(playerId)
            return
        self.NotifyToClient(playerId, ModuleEvent.ModuleRequestSynDialogDataEvent, {
            "data": ModuleDialog.DialogData
        })

    def OnKeyPressInGame(self, args):
        playerId, isDown, key = super(DialogModuleServer, self).OnKeyPressInGame(args)
        if not isDown:
            return
        # if key == KeyBoardType.KEY_F:
        #     self.CreateDialog(playerId, "demo_dialog_control", {})
