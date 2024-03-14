# -*- coding:utf-8 -*-


from ....server.entity.player_entity import *


class DialogEntity(LivingEntity):
    """对话实体"""

    def __init__(self, entityId):
        super(DialogEntity, self).__init__(entityId)
        self.system = MDKConfig.GetModuleServer()  # type: MDKConfig.GetModuleServerSystemCls()

    def __del__(self):
        print "[warn]", "del %s" % self.__class__.__name__
        pass

    # -----------------------------------------------------------------------------------

    def ParseDialog(self, config, context=None):
        """解析对话配置"""
        dialog_type = config["type"]

        if dialog_type == "dialog_control":
            trigger = self.ParseDialogControl(config)
        return lambda args=context: trigger(args)

    # -----------------------------------------------------------------------------------

    def ParseDialogControl(self, config):
        # type: (dict) -> any
        """解析对话控制"""
        initial_state = config["initial_state"]
        if initial_state not in config:
            print "[warn]", "Invalid initial_state: %s" % initial_state
            return lambda _: None
        return lambda context: self.ParseDialogContext(config, initial_state)(context)

    def ParseDialogContext(self, config, state):
        """解析对话内容"""
        dialog = config[state]
        context = dialog["context"]  # type: str
        options = dialog["options"]  # type: list

        def active(args):
            option_map = {}
            for option in options:
                switch = option.split("->")
                # text = switch.pop(0)
                # switch = switch[:1]
            # -----------------------------------------------------------------------------------
            pack = {
                "context": context,
                "options": option_map
            }

        return lambda _context: active(_context)

    # -----------------------------------------------------------------------------------

    @classmethod
    def GetTargetValue(cls, key, config, context):
        # type: (str, dict, dict) -> any
        """获得目标数据"""
        value = config[key]
        if isinstance(value, str) and value.startswith("context"):
            key = value.split(".")[-1]
            return context.get(key)
        return value

    def GetTargetId(self, target, context):
        # type: (str, dict) -> str
        """
        获得目标Id\n
        - self: str
        - context: str
        """
        if target.startswith("context"):
            key = target.split(".")[-1]
            return context.get(key)
        return self.id
