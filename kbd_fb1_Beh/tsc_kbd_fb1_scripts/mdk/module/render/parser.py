# -*- coding:utf-8 -*-


from const import ModuleEnum
from ..system.parser.base import SimpleObjLoadParser


class RenderParser(SimpleObjLoadParser):
    """对话解析器"""
    __mVersion__ = 3
    __identifier__ = ModuleEnum.parser_identifier
    DataMergeMode = 1

    @classmethod
    def Parser(cls, config, root, pack):
        head_path = "/".join(root.split("/")[:-1])

        res = {"global": {}, "player": {}, "mob": {}}

        # 全局数据
        data_key = "global"
        for key in config.get(data_key, []):
            path = head_path + "/%s" % key
            data = cls.LoadModConfig(path)
            if data:
                res[data_key].update(data)

        # 玩家数据
        data_key = "player"
        for key in config.get(data_key, []):
            path = head_path + "/%s" % key
            data = cls.LoadModConfig(path)
            if data:
                res[data_key].update(data)

        # 生物数据
        data_key = "mob"
        for engine_type, path_list in config.get(data_key, {}):
            if not path_list:
                continue
            res[data_key][engine_type] = {}
            for key in path_list:
                path = head_path + "/%s" % key
                data = cls.LoadModConfig(path)
                if data:
                    res[data_key][engine_type].update(data)
        return res

    @classmethod
    def Build(cls, pack):
        global_render = pack.get("global", {})
        if global_render:
            player_render = pack.get("player", {})
            # 将全局渲染资源合并到玩家的渲染内
            cls.MergeData(global_render, player_render)
        return pack

    @classmethod
    def MergeData(cls, src, des):
        # type: (dict, dict) -> None
        """递归合并数据"""
        for key in src.iterkeys():
            des.update({key: src[key]})
