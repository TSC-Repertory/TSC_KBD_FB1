# -*- coding:utf-8 -*-


from ..system.parser.base import GameParser


class LootParser(GameParser):
    """战利品解析器"""
    __mVersion__ = 1
    __identifier__ = "loot"

    @classmethod
    def Parser(cls, config, root, pack):
        head_path = "/".join(root.split("/")[:-1])
        res = {}

        additions = {}
        for line in config["data"]:
            path = head_path + "/%s" % line
            data = cls.LoadModConfig(path)
            if not data:
                continue
            for key in data.keys():
                # merge key
                if key.startswith("@"):
                    merge_data = data.pop(key)  # type: dict
                    merge_key = key.replace("@", "")
                    add_data = additions.get(merge_key, [])
                    add_data.extend(merge_data)
                    additions[merge_key] = merge_data
            # add data
            res.update(data)
        # -----------------------------------------------------------------------------------
        """merge data"""
        for key, data in additions.iteritems():
            if key in res:
                res[key].extend(data)
            else:
                # create new data
                res[key] = data
        return res


class VanillaLoot(GameParser):
    """原版战利品解析器"""
    __mVersion__ = 1
    __identifier__ = "vanilla_loot"

    @classmethod
    def Parser(cls, config, root, pack):
        head_path = "/".join(root.split("/")[:-1])
        res = {}

        additions = {}
        for line in config["data"]:
            path = head_path + "/%s" % line
            data = cls.LoadModConfig(path)
            if not data:
                continue
            for key in data.keys():
                # merge key
                if key.startswith("@"):
                    merge_data = data.pop(key)  # type: dict
                    merge_key = key.replace("@", "")
                    add_data = additions.get(merge_key, [])
                    add_data.extend(merge_data)
                    additions[merge_key] = merge_data
            # add data
            res.update(data)
        # -----------------------------------------------------------------------------------
        """merge data"""
        for key, data in additions.iteritems():
            if key in res:
                res[key].extend(data)
            else:
                # create new data
                res[key] = data
        return res
