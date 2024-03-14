# -*- coding:utf-8 -*-


from ..system.parser.base import GameParser


class TagParser(GameParser):
    """标签解析器"""
    __mVersion__ = 1
    __identifier__ = "tag"
    _tag_storage = {}

    def __init__(self):
        super(TagParser, self).__init__()

    @classmethod
    def Parser(cls, config, root, pack):
        head_path = "/".join(root.split("/")[:-1])

        for line in config["data"]:
            path = head_path + "/%s" % line
            data = cls.LoadModConfig(path)
            if not data:
                continue
            replace = data.get("replace", False)
            tags = data["values"]
            cls._tag_storage[path] = tags
        # -----------------------------------------------------------------------------------
        return cls._tag_storage
