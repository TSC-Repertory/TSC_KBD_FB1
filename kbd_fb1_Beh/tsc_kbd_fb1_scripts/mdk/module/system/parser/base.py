# -*- coding:utf-8 -*-


import copy

import mod.client.extraClientApi as clientApi


class GameParser(object):
    """游戏解析器"""
    __mVersion__ = 4
    __identifier__ = "parser"
    DataMergeMode = 0  # 数据合并模式：0 update | 1 递归子键字典合并

    @classmethod
    def Parser(cls, config, root, pack):
        # type: (dict, str, dict) -> any
        """解析数据"""

    @classmethod
    def Build(cls, pack):
        # type: (dict) -> dict
        """构造数据"""
        return pack

    @classmethod
    def LoadModConfig(cls, path):
        # type: (str) -> dict
        """导入数据"""
        return clientApi.GetModConfigJson("modconfigs/" + path)

    @classmethod
    def GetId(cls):
        """获得解析器Id"""
        return cls.__identifier__


class SimpleObjLoadParser(GameParser):
    """简单对象导入解释器"""
    __mVersion__ = 1

    @classmethod
    def Parser(cls, config, root, pack):
        head_path = "/".join(root.split("/")[:-1])
        res = {}
        for line in config["data"]:
            path = head_path + "/%s" % line
            data = cls.LoadModConfig(path)
            if data:
                res.update(data)
        return res


class PathOrientedParser(GameParser):
    """
    路径主导解析器\n
    - 数据键以配置文件的路径
    - 数据为整个文件的内容
    """
    __mVersion__ = 2

    @classmethod
    def Parser(cls, config, root, pack):
        head_path = "/".join(root.split("/")[:-1])
        res = {}
        for line in config["data"]:
            path = head_path + "/%s" % line
            data = cls.LoadModConfig(path)
            if data:
                key = "/".join(path.split("/")[1:]).replace(".json", "")
                data = cls.Modify(data)
                res.update({key: data})
        return res

    @classmethod
    def Modify(cls, data):
        # type: (any) -> dict
        """数据修正"""


class InheritBuildParser(SimpleObjLoadParser):
    """继承式构造解释器"""
    __mVersion__ = 3

    @classmethod
    def CheckKeyAvailable(cls, key):
        # type: (str) -> bool
        """检测键是否有效"""
        return True

    @classmethod
    def Build(cls, pack):
        print "[info]", "building %s data" % cls.GetId()
        parsed_data = {}

        for i in xrange(60):
            if not pack:
                # print "[info]", "finished build %s -> %d" % (cls.GetId(), i + 1)
                return parsed_data
            for key, config in pack.items():
                if not cls.CheckKeyAvailable(key):
                    pack.pop(key, None)
                    continue
                if ":" not in key:
                    data = pack.pop(key)
                    parsed_data[key] = data
                    continue
                obj_id, base_on_id = key.split(":")
                base_on_config = parsed_data.get(base_on_id)  # type: dict
                if not base_on_config:
                    continue
                obj_config = copy.deepcopy(base_on_config)
                obj_config.update(config)
                pack.pop(key)
                parsed_data[obj_id] = obj_config
        print "[warn]", "以下内容无法解析："
        for key in pack.keys():
            print "[info]", key
        return {}
