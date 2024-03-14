# -*- coding:utf-8 -*-


import re

from const import *
from ..system.base import *
from ..system.preset import LoadConfigModuleServer
from ...common.system.event import ServerDefaultEvent
from ...common.utils.misc import Misc, Eval
from ...server.entity import RawEntity

"""
属性模块服务端：
- 玩家属性加载时刻：ClientLoadAddonsFinishServerEvent
"""


class AttrKeyTransformer(object):
    """保留字转换"""

    @staticmethod
    def GetSetFromPatten(target):
        # type: (str) -> set
        resSet = set()
        patten = re.findall("%(.*?)%", target)[0]
        rangeType = re.findall(r"\[(\d+)-(\d+)]", patten)

        # Patten-1:  %[min-max]%
        if rangeType:
            minV, maxV = map(int, rangeType[0])
            maxV += 1
            for index in range(minV, maxV):
                resSet.add(re.sub("%(.*?)%", str(index), target))
        return resSet

    @classmethod
    def GetModifyAttrKey(cls, target):
        # type: (str) -> set
        """
        属性键处理\n
        - "entity%[1-3]%" -> {"entity1", "entity2", "entity3"}
        """
        attrSet = set()
        for attKey in target.split(" "):
            if re.findall("%.*?%", attKey):
                attrSet.update(cls.GetSetFromPatten(attKey))
            else:
                attrSet.add(attKey)
        return attrSet


class AttrBase(object):
    """属性基类"""
    __mVersion__ = 6
    attrDataKey = MDKConfig.ModuleNamespace + "AttrStorage%s" % __mVersion__

    def __init__(self, module):
        self.comp_factory = serverApi.GetEngineCompFactory()

        self._module = weakref.proxy(module)  # type: AttrModuleServer
        self._config = {}
        self._cache = {}
        self._dirty = set()
        self.belong = None
        self._syn_group = set()  # 更新后的属性组，用于仅同步

    def OnDestroy(self):
        """
        销毁实例\n
        - 由属性模块调用
        """
        del self._module
        del self._config
        del self._cache
        del self._dirty

    # -----------------------------------------------------------------------------------

    def GetCache(self):
        return self._cache

    def IsEmpty(self):
        """是否为空属性"""
        return True if not self._config.keys() else False

    # -----------------------------------------------------------------------------------

    def AddDirtyGroup(self, group_key):
        # type: (str) -> None
        """设置数据是否更新"""
        self._dirty.add(group_key)

    def UpdateDirtyGroup(self):
        """更新全部修改属性组"""

    def GetSynGroup(self):
        # type: () -> list
        """获得同步属性组"""
        return list(self._syn_group)

    def ClearSynGroup(self):
        """清除同步属性组"""
        self._syn_group.clear()

    # -----------------------------------------------------------------------------------

    def GetTransFromParam(self, key):
        # type: (str) -> str
        """保留字转换"""
        return key

    # -----------------------------------------------------------------------------------

    @staticmethod
    def _GetGroupDefine(group_key):
        # type: (str) -> dict
        """获得属性组定义 - 只读"""
        group_define = ModuleConfig.GroupDefine.get(group_key)
        if group_define:
            return group_define
        else:
            print "[error]", "属性组定义不存在：", group_key
            return {}

    @staticmethod
    def _GetAttrDefine(attr_key):
        # type: (str) -> dict
        """获得属性组属性定义 - 只读"""
        attr_define = ModuleConfig.AttrDefine.get(attr_key)
        if attr_define:
            return attr_define
        else:
            print "[error]", "属性定义不存在：", attr_key
            return {}

    # -----------------------------------------------------------------------------------

    def __GetJsonAttr(self, group_key, attr_key):
        """获取Json配置属性值"""
        cache = self._cache[group_key]  # type: dict
        if attr_key in cache:
            # print "[suc]", "已经计算:", attr_key
            return True

        config = self._config.get(group_key)  # type: dict
        attributes = config.keys()
        if attr_key not in attributes:
            print "[warn]", "无效属性名:%s <%s>" % (attr_key, group_key)
            return False

        attr_info = config[attr_key]  # type: dict

        # 优先级0：绑定Get函数
        # if "define_get" in self.storage[group_key]["attributes"][attr_key]:
        #     config, funcKey = self.storage[group_key]["attributes"][attr_key]["define_get"]
        #     system = serverApi.GetSystem(*config)
        #     if not hasattr(system, funcKey):
        #         logger.error("[%s]<%s>绑定的系统方法不存在" % (group_key, attr_key))
        #         return ResponseCode.InvalidFunction
        #     attr_value = getattr(system, funcKey)(self.belong)
        #     self.__SetJsonAttr(group_key, attr_key, attr_value)
        #     return ResponseCode.Success

        # 优先级1：使用fix_value的值
        if "fix_value" in attr_info:
            attr_value = attr_info["fix_value"]
            self.__SetJsonAttr(group_key, attr_key, attr_value)
            return True

        # 优先级2：查表
        if attr_info["table"] and attr_info["row"] and attr_info["column"]:
            table_name = "data_" + attr_info["table"]
            if table_name not in ModuleConfig.TableDefine.iterkeys():
                print "[error]", "无效表名:%s attr_info:%s <%s>" % (table_name, attr_key, group_key)
                return False
            row_key = attr_info["row"]
            row_key = self.GetTransFromParam(row_key)  # 保留字转换

            # 检测是否满足计算条件
            params = re.findall("%(.*?)%", row_key)
            # 无需解析属性 直接计算设置
            if not params:
                return self.__GetValueFromTable(group_key, attr_key, table_name, row_key, attr_info)

            # 解析属性变量
            for param in params:
                # 根据属性名获取该组下的属性Id
                if param in cache.iterkeys():
                    row_key = row_key.replace("%%%s%%" % param, str(cache[param]))

            # 替换完后再检测一次
            params = re.findall("%(.*?)%", row_key)
            if not params:
                return self.__GetValueFromTable(group_key, attr_key, table_name, row_key, attr_info)

            # 继续逐一获取属性数据
            for param in params:
                # 检测未解析的变量是否属于该属性组
                if param not in attributes:
                    print "[warn]", "公式存在无法解析的属性:%s <%s>" % (param, group_key)
                    return False
                self.__GetJsonAttr(group_key, param)  # 逐一获取该属性
            return self.__GetJsonAttr(group_key, attr_key)

        # 优先级3：公式
        elif attr_info.get("formula"):
            formula = str(attr_info.get("formula"))
            # 检测是否满足计算条件
            for _ in xrange(3):
                # 无参数解析 简单直接计算设置
                params = re.findall("%(.*?)%", formula)
                if not params:
                    # print "[suc]", "1无需解析属性 直接计算设置", attr_key
                    return self.__GetValueFromFormula(group_key, attr_key, formula)
                for param in params:
                    # 如果已经被计算出来的 则提替对应数值
                    if param not in attributes:
                        print "[error]", "公式存在无法解析的属性:", param, "使用缺省值：0"
                        cache[param] = 0
                    if param in cache.iterkeys():
                        formula = formula.replace("%%%s%%" % param, str(cache[param]))
                        # print "[debug]", "公式替换新值：检测是否完成"
                        if not re.findall("%(.*?)%", formula):
                            # print "[suc]", "完成替换，计算公式"
                            return self.__GetValueFromFormula(group_key, attr_key, formula)
                    # 逐一获取该属性
                    # print "[debug]", "[x]逐一获取该属性:", param
                    if self.__GetJsonAttr(group_key, param):
                        # print "[suc]", "解析到新的属性，更新缓存"
                        cache = self._cache[group_key]
                        formula = formula.replace("%%%s%%" % param, str(cache[param]))
            return self.__GetJsonAttr(group_key, attr_key)

        # 优先级4：基础值
        elif "base" in attr_info:
            attr_value = attr_info.get("base")
            # print "[warn]", "获得基础值:", attr_key, attr_value
            self.__SetJsonAttr(group_key, attr_key, attr_value)
            return True

        # 缺省值：0
        else:
            print "[warn]", "属性%s<%s>使用缺省值0" % (attr_key, group_key)
            self.__SetJsonAttr(group_key, attr_key, 0)
            return True

    def __SetJsonAttr(self, group_key, attr_key, attr_value):
        self._cache[group_key][attr_key] = self.__UseDefineSet(group_key, attr_key, attr_value)

    def __GetValueFromFormula(self, group_key, attr_key, formula):
        try:
            attr_value = Eval.Run(formula)
        except Exception as err:
            print "[warn]", "%s 公式计算出错:%s" % (err, formula)
            attr_value = 0
        self.__SetJsonAttr(group_key, attr_key, attr_value)

    def __GetValueFromTable(self, group_key, attr_key, table_name, row, attr_info):
        column = attr_info.get("column")
        table_info = ModuleConfig.TableDefine[table_name]  # type: dict
        row_info = table_info.get(row)  # type: dict
        if not isinstance(row_info, dict):
            print "[error]", "无效行键:%s <%s>" % (row, table_name)
            return False
        if column not in row_info.iterkeys():
            print "[error]", "无效列键:%s <%s>" % (column, table_name)
            return False

        attr_value = row_info[column]
        self.__SetJsonAttr(group_key, attr_key, attr_value)
        return True

    def __UseDefineSet(self, group_key, attr_key, attr_value):
        if not self._config[group_key][attr_key].get("define_set"):
            return attr_value

        config, funcKey = self._config[group_key][attr_key]["define_set"]
        system = serverApi.GetSystem(*config)
        if not hasattr(system, funcKey):
            return 0
        return getattr(system, funcKey)(self.belong, attr_value)

    def __UseDefineGet(self, group_key, attr_key):
        pass

    # -----------------------------------------------------------------------------------

    """属性组相关"""

    def _CanAddGroup(self, group_key):
        # type: (str) -> bool
        """判断是否可以添加属性组"""

    def _UpdateGroupAttr(self, group_key):
        # type: (str) -> None
        """
        更新属性组属性\n
        - 更新完保存至缓存
        """
        if group_key not in self._config:
            self._dirty.discard(group_key)
            return
        self._cache[group_key] = {}
        for attr_key in self._config[group_key].iterkeys():
            self.GetAttr(group_key, attr_key)
        self._dirty.discard(group_key)
        self._syn_group.add(group_key)

    @classmethod
    def __InitGroup(cls, group_key):
        # type: (str) -> dict
        """
        初始化属性组属性\n
        - group_key: str
            - attr_name: str
                - id: str
                - name: str
                - base: float
                - formula: str
                - table: str
                - row: str
                - column: str
        """
        config = {}
        group_define = cls._GetGroupDefine(group_key)
        for attr_key in group_define["attributes"]:
            attr_define = cls._GetAttrDefine(attr_key)
            attr_name = attr_define["name"]
            config[attr_name] = attr_define.copy()
        return config

    def AddGroup(self, group_key):
        # type: (str) -> bool
        """添加属性组"""
        if self._CheckGroup(group_key):
            return False
        if not self._CanAddGroup(group_key):
            return False
        self._config[group_key] = self.__InitGroup(group_key)
        self._cache[group_key] = {}
        self.AddDirtyGroup(group_key)

    def DelGroup(self, group_key):
        # type: (str) -> bool
        """删除属性组"""
        if not self._CheckGroup(group_key):
            return False
        self._config.pop(group_key, None)
        self._cache.pop(group_key)
        self.AddDirtyGroup(group_key)

    def GetGroup(self, group_key):
        # type: (str) -> dict
        """获得属性组全部属性"""
        if not self._CheckGroup(group_key):
            return {}
        if group_key in self._dirty:
            self._UpdateGroupAttr(group_key)
        return self._cache[group_key]

    def _CheckGroup(self, group_key):
        # type: (str) -> bool
        """判断属性组是否存在"""
        return group_key in self._config

    # -----------------------------------------------------------------------------------

    """属性相关"""

    def _CheckAttr(self, group_key, attr_key):
        # type: (str, str) -> bool
        """判断指定属性组属性是否存在"""
        if not self._CheckGroup(group_key):
            return False
        config = self._config[group_key]  # type: dict
        return attr_key in config.iterkeys()

    def AddAttr(self, group_key, attr_name):
        # type: (str, str) -> bool
        """指定属性组添加属性"""
        if not self._CheckGroup(group_key):
            return False

        config = self._config[group_key]  # type: dict
        if config.get(attr_name):
            return False

        attr_key = AttrModuleServer.GetAttrKeyByName(group_key, attr_name)
        config[attr_name] = self._GetAttrDefine(attr_key).copy()
        self._config[group_key] = config
        self.AddDirtyGroup(group_key)
        return True

    def DelAttr(self, group_key, attr_key):
        # type: (str, str) -> bool
        """指定属性组删除属性"""
        if not self._CheckAttr(group_key, attr_key):
            return False

        group = self._config[group_key]  # type: dict
        group.pop(attr_key)
        self._config[group_key] = group
        group = self._cache[group_key]  # type: dict
        group.pop(attr_key)
        self._cache[group_key] = group

        self.AddDirtyGroup(group_key)
        return True

    def GetAttr(self, group_key, attr_key):
        # type: (str, str) -> any
        """获得指定属性组属性"""
        if not self._CheckGroup(group_key):
            print "[error]", "属性组不存在：", group_key
            return False
        if group_key not in self._dirty:
            return self._cache[group_key][attr_key]
        try:
            self.__GetJsonAttr(group_key, attr_key)
            return self._cache[group_key][attr_key]
            # print "[debug]", "%s: %s" % (attr_key, attr_value)
        except RuntimeError:
            print "[warn]", "无法获得属性:%s<%s> (属性可能不存在)" % (attr_key, group_key)
            return None

    def SetAttr(self, group_key, attr_key, value):
        # type: (str, str, any) -> bool
        """
        设置指定属性组属性值
        - SetAttr之后的值不再由配置文件决定
        """
        if not self._CheckAttr(group_key, attr_key):
            return False

        config = self._config[group_key]
        config[attr_key]["fix_value"] = value
        self.AddDirtyGroup(group_key)
        return True

    def ResetAttr(self, group_key, attr_key):
        # type: (str, str) -> bool
        """重置属性固定值"""
        if not self._CheckAttr(group_key, attr_key):
            return False

        config = self._config[group_key]
        config[attr_key].pop("fix_value", None)
        self.AddDirtyGroup(group_key)
        return True

    # -----------------------------------------------------------------------------------

    def DefineGetAttr(self, group_key, attr_key, func):
        # type: (str, str, any) -> bool
        """定义获取属性组属性时修正函数"""
        if not self._CheckGroup(group_key):
            return False

    def DefineSetAttr(self, group_key, attr_key, func):
        # type: (str, str, any) -> bool
        """定义设置属性组属性时修正函数"""
        if not self._CheckGroup(group_key):
            return False


class AttrEntity(AttrBase):
    """实体属性基类"""
    __mVersion__ = 4

    _group_pass_map = {}  # 实体类型的属性组可添加对应

    def __init__(self, module, entityId):
        super(AttrEntity, self).__init__(module)
        self.id = entityId
        self.belong = self.id  # 所属：生物实体Id
        self.data_comp = self.comp_factory.CreateExtraData(self.id)
        self.game_comp = self.comp_factory.CreateGame(self.id)
        self.engine_type = self.comp_factory.CreateEngineType(self.id).GetEngineTypeStr()

        self._load_data = False

        self.LoadDataConfig()

    def __del__(self):
        pass
        # print "[warn]", "destroy:", self.__class__.__name__, self.id

    # -----------------------------------------------------------------------------------

    def _CanAddGroup(self, group_key):
        # type: (str) -> bool
        """判断是否可以添加属性组"""
        type_config = self._module.GetGroupTypeConfig()  # type: dict
        config = type_config.get(group_key)  # type: dict
        if not config:
            return False
        if self.engine_type not in self._group_pass_map:
            self._group_pass_map[self.engine_type] = {}
        pass_map = self._group_pass_map[self.engine_type]  # type: dict
        if group_key in pass_map:
            return pass_map.get(group_key)
        if config.get("all_pass"):
            pass_map[group_key] = True
            return True
        white_list = config.get("white_list")
        if white_list:
            is_pass = self.engine_type in white_list
            pass_map[group_key] = is_pass
            return is_pass
        black_list = config.get("black_list")
        if black_list:
            is_pass = self.engine_type not in black_list
            pass_map[group_key] = is_pass
            return is_pass
        pass_map[group_key] = False
        return False

    def LoadDataConfig(self):
        """导入数据配置"""
        storage = self.GetDataConfig()
        if storage:
            self._config = storage
            for group_key, config in self._config.items():
                # 判断是否有更新数据键
                if self._module.GetGroupAttrNum(group_key) != len(config):
                    has_key = set(attr["id"] for attr in config.values())  # attr_name
                    all_key = set(self._GetGroupDefine(group_key)["attributes"])
                    for attr_key in all_key.difference(has_key):
                        AttrDefine = self._GetAttrDefine(attr_key)
                        attr_name = AttrDefine["name"]
                        config[attr_name] = AttrDefine.copy()
                        print "[info]", "补充新属性：%s <%s>" % (attr_name, group_key)
                self._cache[group_key] = {}
                self.AddDirtyGroup(group_key)
            return
        for group_key in self._module.GetGroupTypeConfig():
            self.AddGroup(group_key)

    def AddDirtyGroup(self, group_key):
        super(AttrEntity, self).AddDirtyGroup(group_key)
        self._module.AddOptUpdateEntity(self.id)

    def _UpdateGroupAttr(self, group_key):
        super(AttrEntity, self)._UpdateGroupAttr(group_key)
        self._module.AddSaveDataEntity(self.id)
        if not self._dirty:
            self._module.DelOptUpdateEntity(self.id)

    def UpdateDirtyGroup(self):
        for group_key in list(self._dirty):
            self._UpdateGroupAttr(group_key)

    # -----------------------------------------------------------------------------------

    def SaveDataConfig(self):
        self.data_comp.SetExtraData(AttrBase.attrDataKey, self._config)

    def GetDataConfig(self):
        # type: () -> dict
        """获得实体数据"""
        storage = self.data_comp.GetExtraData(AttrBase.attrDataKey)
        if not storage or not isinstance(storage, dict):
            return {}
        return storage


class AttrModuleServer(LoadConfigModuleServer):
    """属性模块服务端"""
    __identifier__ = ModuleEnum.identifier
    __mVersion__ = 8
    _ModuleRequestRegisterEvent = ModuleEvent.ModuleRequestAttributeRegisterEvent

    _AttrNameKeyMap = {}
    _GroupAttrNumMap = {}  # 属性组包含的属性数量

    def __init__(self):
        super(AttrModuleServer, self).__init__()
        self._entity_storage = {}
        self._load_data = False

        self._syn_player = set()
        self._syn_black_list = set()
        self._entity_black_list = set()

        # 属性组类型定义配置 group_key: {"all_pass": bool, "white_list": list, "black_list": list}
        self._group_type_config = {}

        self._dirt_entity = set()
        self._save_entity = set()
        self._opt_update = set()

    def OnDestroy(self):
        for attrEntity in self._entity_storage.itervalues():
            attrEntity.OnDestroy()
        del self._entity_storage
        del ModuleConfig.GroupDefine
        del ModuleConfig.AttrDefine
        del ModuleConfig.TableDefine
        super(AttrModuleServer, self).OnDestroy()

    def ConfigEvent(self):
        super(AttrModuleServer, self).ConfigEvent()
        self.defaultEvent.update({
            ServerDefaultEvent.OnScriptTickServer: self.OnScriptTickServer,
            ServerDefaultEvent.AddEntityServerEvent: self.AddEntityServerEvent,
            ServerDefaultEvent.EntityRemoveEvent: self.EntityRemoveEvent,
            ServerDefaultEvent.PlayerIntendLeaveServerEvent: self.PlayerIntendLeaveServerEvent,
        })
        self.clientEvent.update({
            ModuleEvent.ModuleRequestEntityAttrEvent: self.ModuleRequestEntityAttrEvent
        })

    # -----------------------------------------------------------------------------------

    @staticmethod
    def GetEntityCls():
        """获得属性实体类"""
        return AttrEntity

    def GetEntityIns(self, entityId):
        # type: (str) -> AttrEntity
        attrEntity = self._entity_storage.get(entityId)  # type: AttrEntity
        return attrEntity

    @classmethod
    def GetAttrKeyByName(cls, group_key, attr_name):
        # type: (str, str) -> str
        """根据属性名获得属性Id"""
        config = cls._AttrNameKeyMap.get(group_key, {})  # type: dict
        return config.get(attr_name, "")

    @classmethod
    def GetGroupAttrNum(cls, group_key):
        # type: (str) -> int
        """
        获得属性组属性数量\n
        - 用来简易判断是否有新属性更新
        """
        return cls._GroupAttrNumMap.get(group_key, 0)

    # -----------------------------------------------------------------------------------

    def GetEntityAttrGroup(self, entityId, group_key):
        # type: (str, str) -> dict
        """获得实体属性"""
        config = self._entity_storage.get(entityId)  # type: dict
        if not config:
            return {}
        return config.get(group_key, {})

    def GetItemAttr(self, item):
        # type: (dict) -> dict
        """获得物品属性"""

    def AddEntitySynBlackList(self, engine_type):
        # type: (str) -> None
        """添加实体同步黑名单"""
        self._syn_black_list.add(engine_type)

    def AddAttrEntityBlackList(self, engine_type):
        # type: (str) -> None
        """添加属性实体黑名单"""
        self._entity_black_list.add(engine_type)

    def RegisterPlayer(self, playerId):
        # type: (str) -> None
        """注册玩家监听客户端同步"""
        self._syn_player.add(playerId)

    def UnRegisterPlayer(self, playerId):
        # type: (str) -> None
        """反注册玩家家庭客户端同步"""
        self._syn_player.discard(playerId)

    def AddOptUpdateEntity(self, entityId):
        # type: (str) -> None
        """添加优化更新实体"""
        self._opt_update.add(entityId)

    def DelOptUpdateEntity(self, entityId):
        # type: (str) -> None
        """删除优化更新实体"""
        self._opt_update.discard(entityId)

    def AddSaveDataEntity(self, entityId):
        # type: (str) -> None
        """添加需要保存数据的实体"""
        self._save_entity.add(entityId)

    # -----------------------------------------------------------------------------------

    def GetGroupTypeConfig(self):
        """获得属性组类型定义配置"""
        return self._group_type_config

    def InitAttrEntity(self, entityId):
        """
        初始化属性实体\n
        - 成功会保存至缓存和同步客户端
        - 失败不保存
        """
        # Todo: 判断是否有任何属性数据，需要处理类似技能实例（无任何属性组却占用了遍历资源）
        entity = AttrEntity(self, entityId)
        if entity.IsEmpty():
            print "[info]", "生物属性数据为空：", entity.engine_type
            return
        self._entity_storage[entityId] = entity

    # -----------------------------------------------------------------------------------

    def OnLoadModConfig(self, data):
        pass_key = {"attribute_groups", "attributes"}
        if pass_key & set(data.keys()) != pass_key:
            print "[warn]", "属性配置不符合条件"
            self.BatchUnListenDefault(self.defaultEvent)
            self.BatchUnListenBaseClient(self.clientEvent)
            return True
        # -----------------------------------------------------------------------------------
        """属性组数据处理

        属性组数据配置格式:
        - name: str 属性组Id
        - bind_player: bool 是否绑定玩家
        - bind_type: str 绑定类型 [entity|player|item]
        - white_list: str 绑定白名单
        - black_list: str 绑定黑名单
        - attributes: str 绑定属性集合
        """
        group_data = data.pop("attribute_groups", {})
        Misc.CleanDictByMatch(group_data, "comment")
        # 类型绑定预处理
        pass_key = ["entity", "player", "item"]
        for group_key, config in group_data.iteritems():
            assert isinstance(config, dict)
            bind_type = config.pop("bind_type", None)
            if bind_type not in pass_key:
                print "[error]", "Invalid bind_type:%s -> <group_key:%s>" % (bind_type, group_key)
                continue
            type_config = {}
            white_set = config.pop("white_list", "")
            black_set = config.pop("black_list", "")
            if bind_type == "entity":
                type_config["all_pass"] = False
                # Todo: 黑白名单分割规范
                if white_set:
                    type_config["white_list"] = list(set(white_set.split(":")))
                elif black_set:
                    type_config["black_list"] = list(set(black_set.split(":")))
                else:
                    type_config["all_pass"] = True  # 无黑白名单默认无条件通过
            elif bind_type == "player":
                type_config = {"white_list": "minecraft:player"}
            # Todo: 绑定物品类型处理
            self._group_type_config[group_key] = type_config
            # 属性列表修正 -> set
            row_attributes = config["attributes"]
            config["attributes"] = AttrKeyTransformer.GetModifyAttrKey(row_attributes)
            self._GroupAttrNumMap[group_key] = len(config["attributes"])
        ModuleConfig.GroupDefine = group_data
        print "[suc]", "已加载属性组：%s" % len(ModuleConfig.GroupDefine)
        # -----------------------------------------------------------------------------------
        """属性数据处理

        属性数据配置格式:
        - id: str           属性Id
        - name: str         属性名称
        - base: float       属性基础值
        - formula: str      属性公式
        - table: str        属性表格名称
        - row: str          属性表格行名
        - column: str       属性表格列名
        - item_tips: str    属性在物品上的信息显示
        """
        attr_data = data.pop("attributes", {})
        Misc.CleanDictByMatch(attr_data, "comment")
        ModuleConfig.AttrDefine = attr_data
        print "[suc]", "已加载属性：%s" % len(ModuleConfig.AttrDefine)
        # -----------------------------------------------------------------------------------
        for group_key, config in ModuleConfig.GroupDefine.iteritems():
            self._AttrNameKeyMap[group_key] = {}
            for attr_key in config["attributes"]:
                attr_config = attr_data[attr_key]
                attr_name = attr_config["name"]
                # 建立属性组的属性名于属性Id结构
                self._AttrNameKeyMap[group_key][attr_name] = attr_key
        # -----------------------------------------------------------------------------------
        """属性数据表处理

        数据表数据配置格式:
        - 无特定格式，需要保证属性数据使用表格的<row><column>能定位到值即可
        - 数值类型默认使用float
        """
        for key, table in data.iteritems():
            if key.startswith("data_") and isinstance(table, dict):
                ModuleConfig.TableDefine[key] = table
        print "[suc]", "已加载数据表：%s" % len(ModuleConfig.TableDefine)
        # -----------------------------------------------------------------------------------
        self._load_data = True
        # print "[info]", "完成属性数据配置"
        # 完成加载后首次处理数据
        for entityId in list(self._dirt_entity):
            self.InitAttrEntity(entityId)
        self._dirt_entity.clear()
        return False

    def OnUpdateSecond(self):
        print "实体实例数量：%s" % len(self._entity_storage)

    # -----------------------------------------------------------------------------------

    def OnScriptTickServer(self):
        if self._opt_update:
            entityId = self._opt_update.pop()
            entity = self._entity_storage.get(entityId)  # type: AttrEntity
            if entity:
                entity.UpdateDirtyGroup()
                cache = entity.GetCache()  # type: dict
                self.BroadcastToAllClient(ModuleEvent.ModuleRequestSynEntityAttrEvent, {
                    "entityId": entityId,
                    "data": {group_key: cache[group_key] for group_key in entity.GetSynGroup()}
                })
                entity.ClearSynGroup()
        if self._save_entity:
            for entityId in self._save_entity:
                entity = self._entity_storage.get(entityId)  # type: AttrEntity
                if entity:
                    entity.SaveDataConfig()
            self._save_entity.clear()

    def AddEntityServerEvent(self, args):
        entityId = args.get("id")
        if not RawEntity.IsMob(entityId):
            return
        if not self._load_data:
            self._dirt_entity.add(entityId)
            return
        self.InitAttrEntity(entityId)

    def EntityRemoveEvent(self, args):
        entityId = args["id"]
        self._dirt_entity.discard(entityId)
        entity = self._entity_storage.pop(entityId, None)
        if entity:
            entity.OnDestroy()

    def PlayerIntendLeaveServerEvent(self, args):
        playerId = args["playerId"]
        self._dirt_entity.discard(playerId)
        entity = self._entity_storage.pop(playerId, None)
        if entity:
            entity.OnDestroy()

    def ClientLoadAddonsFinishServerEvent(self, args):
        playerId = args["playerId"]
        if not self._load_data:
            self._dirt_entity.add(playerId)
            return
        self.InitAttrEntity(playerId)

    def ModuleRequestEntityAttrEvent(self, args):
        playerId = args["playerId"]
        entityId = args["entityId"]
        entity = self._entity_storage.get(entityId)
        if entity:
            self.NotifyToClient(playerId, ModuleEvent.ModuleRequestSynEntityAttrEvent, {
                "entityId": entityId,
                "data": entity.GetCache()
            })
