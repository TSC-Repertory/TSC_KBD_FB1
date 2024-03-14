# -*- coding:utf-8 -*-


import copy
import random
import weakref

from const import *
from ..system.parser.base import PathOrientedParser
from ...common.system.base import *
from ...common.utils.misc import Misc
from ...server.entity import RawEntity
from ...server.item.base import ServerItem


class PredicateParser(PathOrientedParser):
    """断言解析器"""
    __mVersion__ = 2
    __identifier__ = ModuleEnum.identifier

    @classmethod
    def Modify(cls, data):
        if isinstance(data, list):
            return {"condition": ConditionEnum.default, "terms": data}
        return data


class BaseParser(object):
    """基础解析器"""
    __mVersion__ = 1

    def __init__(self, context):
        self.comp_factory = serverApi.GetEngineCompFactory()
        self.game_comp = self.comp_factory.CreateGame(serverApi.GetLevelId())
        from event import EventParserBase
        assert isinstance(context, dict)
        self.context = context
        self.owner = None  # type: EventParserBase
        self._funcParser = None
        self._conditionParser = None
        self._typeParser = None
        self._baseParser = None

    def Parse(self, *args, **kwargs):
        """解析"""

    def GetContextId(self, context=None):
        # type: (dict) -> str
        """获得上下文Id信息"""
        if context:
            target = context.get("target")
            return self.context.get("host") if target == "this" else context.get("target")
        target = self.context.get("target", "this")
        return self.context.get("host") if target == "this" else self.context.get("other").get("id")

    def GetContextPos(self, context=None):
        # type: (dict) -> tuple
        """获得上下文位置信息"""
        interactId = self.GetContextId(context)
        if not interactId:
            interactId = self.context.get("host")
        return RawEntity.GetPos(interactId)

    def SetOwner(self, parser):
        """设置该解析器所属"""
        self.owner = weakref.proxy(parser)

    @classmethod
    def GetStorage(cls, entityId, key):
        # type: (str, str) -> dict
        """获得数据"""
        storage = RawEntity.GetDataComp(entityId).GetExtraData(key)
        if not storage:
            return {}
        return storage

    # -----------------------------------------------------------------------------------

    def GetFunctionParser(self):
        # type: () -> FunctionParser
        """获得函数解释器"""
        return self._funcParser

    def GetConditionParser(self):
        # type: () -> ConditionParser
        """获得条件解释器"""
        return self._conditionParser

    def GetTypeParser(self):
        # type: () -> TypeParser
        """获得类型解析器"""
        return self._typeParser

    def GetBaseParser(self):
        # type: () -> BaseOnParser
        """获取依赖解析器"""
        from event import EventParserBase
        if isinstance(self.owner, EventParserBase):
            return self.owner.GetBaseParser()
        else:
            return self._baseParser


class RangeParser(BaseParser):
    """区间解析器"""
    __mVersion__ = 1

    @classmethod
    def Parse(cls, target):
        """
        区间解析\n
        - type: str 解析方式 默认<constant>
        """
        if not target or not isinstance(target, dict):
            return
        method = target.get("type", RangeType.Uniform)
        if not hasattr(cls, method):
            print "[error]", "无效区间解析类型：", method
            return 0
        return getattr(cls, method)(target)

    @classmethod
    def constant(cls, target):
        # type: (dict) -> any
        """
        常数区间解析\n
        - value: int | float 数量[默认值: 0]
        """
        return target.get("value", 0)

    @classmethod
    def uniform(cls, target):
        # type: (dict) -> any
        """常数区间解析"""
        minV = target.get("min", 0)  # type: float
        maxV = target.get("max", 0)  # type: float

        if minV > maxV:
            print "[error]", "区间解析[minV > maxV] -> ", target
            return 0

        return random.uniform(minV, maxV)

    @classmethod
    def random_int(cls, target):
        # type: (dict) -> int
        """区间整数随机"""
        return int(cls.uniform(target))


class BaseOnParser(BaseParser):
    """依赖解析器"""
    __mVersion__ = 1

    def Parse(self, context):
        # type: (dict) -> any
        """依赖解析"""
        baseType = context.get("base")
        if not hasattr(self, baseType):
            print "[error]", "无效依赖：", baseType
            return 0
        return getattr(self, baseType)(context)

    def health(self, context):
        # type: (dict) -> int
        """
        基于目前生命值\n
        - target: str
        - rate: float
        """
        rate = context.get("rate", 0.5)
        entityId = self.GetContextId(context)
        if not RawEntity.IsAlive(entityId):
            return 0
        attrComp = serverApi.GetEngineCompFactory().CreateAttr(entityId)
        return int(round(attrComp.GetAttrValue(minecraftEnum.AttrType.HEALTH) * rate))

    def max_health(self, context):
        # type: (dict) -> int
        """
        基于最大生命值\n
        - target: str
        - rate: float
        """
        rate = context.get("rate", 0.5)
        entityId = self.GetContextId(context)
        if not RawEntity.IsAlive(entityId):
            return 0
        attrComp = serverApi.GetEngineCompFactory().CreateAttr(entityId)
        return int(round(attrComp.GetAttrMaxValue(minecraftEnum.AttrType.HEALTH) * rate))

    def storage(self, context):
        # type: (dict) -> dict
        """
        基于数据表\n
        - source: str
        - key: str
        - offset: any
        """
        source = context.get("source")
        key = context.get("key")
        entityId = self.GetContextId(context)
        # read-only
        data_comp = self.comp_factory.CreateExtraData(entityId)
        storage = data_comp.GetExtraData(source)  # type: dict
        if not storage:
            return context
        # Todo: 链式索引
        value = storage.get(key)
        offset = context.get("offset")
        if isinstance(offset, dict):
            offset = RangeParser.Parse(offset)
            # Todo: 判断数据类型
            value += offset
        return value


class OperateTypeParser(BaseParser):
    """操作类型解析"""
    __mVersion__ = 1

    @classmethod
    def Parse(cls, context):
        # type: (dict) -> any
        """操作解析"""


class FunctionParser(BaseParser):
    """函数解析器"""
    __mVersion__ = 1

    def Parse(self, context):
        # type: (dict) -> None
        """解析函数修正"""
        functions = context.get("functions", [])  # type: list
        if not functions:
            return

        for function in functions:
            assert isinstance(function, dict)
            funcKey = function.get("function")
            if not hasattr(self, funcKey):
                print "[error]", "无效函数：", funcKey
                continue
            getattr(self, funcKey)(function, context)

    @staticmethod
    def set_count(config, context):
        # type: (dict, dict) -> None
        """
        设置数量\n
        默认值为0，可传字典区间修正解析\n
        - count: int | dict 数量[默认值: 0]
        - limit: bool 是否有上限，否则会限制到[0, 64]
        """
        count = config.get("count", 0)
        if isinstance(count, dict):
            count = RangeParser.Parse(count)
        # 四舍五入值 + 极值修正
        count = int(round(count))
        # 上限值修正
        if "limit" in context:
            limit = context["limit"]  # type: dict
            count = max(limit[0], min(limit[1], count))
        context["count"] = count

    def limit_count(self, config, context):
        # type: (dict, dict) -> None
        """
        限制数量\n
        - 默认设置最大上限\n
        - count: int
        - count: dict
        """
        limit = config.get("count", 1)
        if isinstance(limit, dict):
            _config = (limit.get("min", 0), limit.get("max", 64))
            # 数值修正
            count = context.get("count", 1)
            context["count"] = max(_config[0], min(_config[1], count))
            context["limit"] = _config
        else:
            context["limit"] = (0, limit)

    def set_storage(self, config, context):
        # type: (dict, dict) -> None
        """
        设置自定义数据\n
        - 数据宿主源于target
        """
        entityId = self.GetContextId(context)
        if not entityId:
            print "[error]", "不存在数据源实体"
            return
        data_comp = self.comp_factory.CreateExtraData(entityId)
        for _mConfig in config.get("storages", []):
            assert isinstance(_mConfig, dict)
            storageKey = _mConfig.get("source")
            storage = data_comp.GetExtraData(storageKey)  # type: dict
            if not storage:
                storage = {}
            operate = _mConfig.get("operate", "replace")
            data = _mConfig.get("data", {})
            for key, value in data.items():
                if isinstance(value, dict) and value.get("base"):
                    target = value.get("target")
                    if not target:
                        value["target"] = entityId
                    data[key] = self.GetBaseParser().Parse(value)
            if operate == "merge":
                storage.update(data)
            elif operate == "replace":
                storage = data
            data_comp.SetExtraData(storageKey, storage)

    def add_entity_tag(self, config, context):
        # type: (dict, dict) -> None
        """
        添加实体标签\n
        - 若无上下文的entityId则使用外层target指向目标
        - tag: str
        - tags: list
        """
        entityId = self.GetContextId(context)
        tagComp = self.comp_factory.CreateTag(entityId)
        if "tag" in config:
            tagComp.AddEntityTag(config["tag"])
        if "tags" in config:
            for tag in config["tags"]:
                tagComp.AddEntityTag(tag)

    def set_name(self, config, context):
        # type: (dict, dict) -> None
        """
        设置实体名字\n
        - 若无上下文的entityId则使用外层target指向目标
        - name: str
        """
        engine_type = context["engine_type"]
        name = config.get("name", "")
        # 物品修正
        if engine_type == "minecraft:item":
            context["customName"] = name
            item_comp = self.comp_factory.CreateItem(serverApi.GetLevelId())
            if "lore" in context:
                lore = context["lore"].split("\n")
                lore.insert(0, name)
                context["lore"] = "\n".join(lore)
            return
        entityId = self.GetContextId(context)
        nameComp = self.comp_factory.CreateName(entityId)
        nameComp.SetName(name)

    def set_lore(self, config, context):
        # type: (dict, dict) -> None
        """
        设置文本显示\n
        - lore: str
        """
        lore = config.get("lore", "")
        if isinstance(lore, str):
            lore = lore.split("\n")
        name = context.get("customName")
        if not name:
            name = ServerItem.GetLocalName(context["name"])
        lore.insert(0, name)
        context["lore"] = "\n".join(lore)

    def set_loot_table(self, config, context):
        # type: (dict, dict) -> None
        """
        设置战利品\n
        - type: str
        - name: str
        """
        data = context.get("extraId", {})
        data["loot"] = {
            "type": config.get("type", "custom"),
            "name": config.get("name")
        }
        context["extraId"] = data


class ConditionParser(BaseParser):
    """条件解析器"""
    __mVersion__ = 1

    def Parse(self, target):
        # type: (dict) -> bool
        """解析条件"""
        conditions = target.get("conditions", [])  # type: list
        if not conditions:
            return True
        for condition in conditions:
            assert isinstance(condition, dict)
            conditionId = condition.get("condition")  # type: str
            if not hasattr(self, conditionId):
                print "[error]", "Invalid condition_id：", conditionId
                return False
            conditionRes = getattr(self, conditionId)(condition, target)
            if not conditionRes:
                return False
        # -----------------------------------------------------------------------------------
        return True

    @classmethod
    def random_chance(cls, config, target):
        # type: (dict, dict) -> bool
        """
        随机值判断\n
        - chance: float
        """
        return random.random() <= max(0, min(1, config.get("chance", 0)))

    @classmethod
    def entity_properties(cls, config, target):
        # type: (dict, dict) -> bool
        """
        实体属性测试\n
        - target: str
        - predicate: dict
        """
        print "[debug]", "config -> ", config
        print "[suc]", "target", target
        return True

    @classmethod
    def storage_check(cls, config, target):
        # type: (dict, dict) -> bool
        """
        数据测试\n
        - storage: dict
            - key: str
            - value: str
            - target: str
            - op: str
        """
        entityId = target.get("ownerId")
        _config = config.get("storage")  # type: dict
        if not _config.get("key"):
            print "[error]", "Invalid storage key"
            return False
        if not _config.get("value"):
            print "[error]", "Invalid storage value"
            return False

        data = cls.GetStorage(entityId, _config["key"])
        for key in _config["value"].split("."):
            try:
                data = data.get(key)
            except AttributeError:
                print "[error]", "Invalid storage value:", _config["value"]
                return False
        op = _config.get("op", "")

    def block_state_property(self, config, target):
        # type: (dict, dict) -> bool
        """
        方块测试\n
        - 使用执行者的维度信息
        - block: str
        - properties: dict
        """
        block_name = config.get("block", "")
        block_dim = RawEntity.GetDim(self.owner.host)
        block_pos = self.GetContextPos(target)
        # todo: 方块位置修正
        block_pos = Misc.GetPosModify(block_pos, (0.5, 0.5, 0.5))
        block_comp = self.comp_factory.CreateBlockInfo(serverApi.GetLevelId())
        return block_comp.GetBlockNew(block_pos, block_dim)["name"] == block_name


class TypeParser(BaseParser):
    """类型解析器"""
    __mVersion__ = 2

    def Parse(self, target, assertMap=None):
        # type: (dict, any) -> list
        """
        解析类型\n
        - 可能产生一个或多个结果
        - 返回同类型无条件的配置列表
        """
        objType = target.get("type")
        if not objType or not hasattr(self, objType):
            print "[error]", "无效类型：", objType
            return []
        children = target.get("children", [])  # type: list
        if not children:
            return []
        # -----------------------------------------------------------------------------------
        return getattr(self, objType)(children, assertMap, target)

    def alternative(self, children, assertMap, config):
        # type: (list, any, dict) -> list
        """
        条件处理\n
        - 从子项目中选取第一个满足条件的，这些子项目通常都指定了条件
        """

        conditionParer = self.owner.GetConditionParser()
        for child in children:
            assert isinstance(child, dict)
            if conditionParer.Parse(child):
                if assertMap and not assertMap(child):
                    continue
                child.pop("conditions", None)
                return [child]
        return []

    def group(self, children, assertMap, config):
        # type: (list, any, dict) -> list
        """
        分组处理\n
        - 从所有满足条件的子项目中随机选取，逻辑和随机池类似。
        - 子项目通过weight来决定权重，默认权重为1
        """
        _map = {}
        _weights = {}
        rolls = config.get("rolls")
        if rolls:
            if isinstance(rolls, dict):
                rolls = int(RangeParser.Parse(rolls))
        else:
            rolls = 1
        conditionParer = self.owner.GetConditionParser()

        storage = []
        for _ in xrange(rolls):
            children = copy.deepcopy(children)
            for index, child in enumerate(children):
                assert isinstance(child, dict)
                if not conditionParer.Parse(child):
                    continue
                if assertMap and not assertMap(child):
                    continue
                child.pop("conditions", None)
                _map[index] = child
                _weights[index] = child.get("weight", 1)
            res = _map.get(Misc.GetRandomFromWeightDict(_weights))
            if isinstance(res, dict):
                res.pop("weight", None)
                if "type" in res:
                    res = self.Parse(res, assertMap)
            if isinstance(res, list):
                storage.extend(res)
            else:
                storage.append(res)
        return storage

    def sequence(self, children, assertMap, config):
        # type: (list, any, dict) -> list
        """
        序列处理\n
        - 从第一个条件不满足的子项目之前的所有的子项目中随机选取
        - 即第一个不满足条件的子项目和之后的子项目会被忽略。
        """
        _map = {}
        _weights = {}
        conditionParer = self.owner.GetConditionParser()
        for index, child in enumerate(children):
            assert isinstance(child, dict)
            if not conditionParer.Parse(child):
                break
            if assertMap and not assertMap(child):
                continue
            child.pop("conditions", None)
            _map[index] = child
            _weights[index] = child.get("weight", 1)
        # -----------------------------------------------------------------------------------
        index = Misc.GetRandomFromWeightDict(_weights)
        res = _map.get(index)
        return [res] if res else []

    @classmethod
    def sample(cls, children, assertMap, config):
        # type: (any, any, dict) -> list
        """随机采样抽取"""
        sample = config.get("sample", 1)
        if isinstance(sample, dict):
            # todo: 暂时只支持RangeParser
            sample = int(RangeParser.Parse(sample))
        if isinstance(children, str):
            if children.startswith("@"):
                matches = children.replace("@", "").split(".")
                if globals().get(matches[0]):
                    target = globals()[matches[0]]
                    for path in matches[1:]:
                        if not hasattr(target, path):
                            print "[error]", "Invalid path: %s" % ".".join(matches)
                            return []
                        target = getattr(target, path)
                    children = target
            else:
                children = getattr(GameItem, children)  # type: list
            if not isinstance(children, list):
                print "[error]", "Invalid children: %s" % children
                return []
        # 最大修正
        max_sample = len(children)
        if max_sample == sample:
            return [{"name": item} for item in children]
        sample = min(sample, max_sample)
        items = random.sample(children, sample)
        return [{"name": item} for item in items]

    @classmethod
    def tag(cls, children, assertMap, config):
        # type: (list, any, dict) -> list
        """
        标签处理\n
        - 从该标签等概率随机选取一个
        - name: str 标签名称
        - expand: bool 为false时选中全部物品
        """
