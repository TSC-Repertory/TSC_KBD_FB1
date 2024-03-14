# -*- coding:utf-8 -*-


import json
import copy
import math
import random
import re
import uuid

"""进入本文件的代码不允许带有非python源库内容"""


class Misc(object):
    __mVersion__ = 3
    _hex_map = {
        "a": 10,
        "b": 11,
        "c": 12,
        "d": 13,
        "e": 14,
        "f": 15
    }

    @staticmethod
    def GetDistBetween(pos1, pos2):
        """获得两点之间距离"""
        return math.sqrt(sum((px - qx) ** 2 for px, qx in zip(pos1, pos2)))

    @staticmethod
    def GetPosModify(pos, extra, **kwargs):
        """获得位置修正"""
        method = kwargs.get("method", "plus")
        if method == "plus":
            return tuple(map(sum, zip(pos, extra)))
        elif method == "sub":
            return tuple(map(lambda x, y: x - y, pos, extra))
        elif method == "time":
            return tuple(map(lambda x: x * extra, pos))
        else:  # multiply
            return tuple(map(lambda x: x[0] * x[1], zip(pos, extra)))

    @staticmethod
    def GetSquareRandomPos(num, start, end):
        # type: (int, tuple, tuple) -> list
        """获得区域随机位置"""
        return [tuple(map(lambda x, y: random.randint(x, y), start, end)) for _ in xrange(num)]

    @staticmethod
    def GetAlignPos(pos):
        # type: (tuple) -> tuple
        """获得校准位置"""
        x, y, z = pos
        if x < 0:
            x -= 1
        if z < 0:
            z -= 1
        return tuple(map(int, (x, y, z)))

    @staticmethod
    def GetRotModify(rot, dx=0.0, dz=0.0):
        """获得转角修正"""
        return Misc.GetPosModify(rot, (dz, dx))

    @staticmethod
    def GetRandomPointFromRadius(pos, r, n=1):
        """获得半径内随机点"""
        posList = []
        for _ in xrange(n):
            theta = random.random() * 2 * math.pi
            radius = random.random() * r
            dx = radius * math.cos(theta)
            dz = radius * math.sin(theta)
            posList.append((int(pos[0] + dx), pos[1], int(pos[2] + dz)))
        return posList

    @staticmethod
    def GetCirclePoint(pos, radius, n=1, offset=0):
        # type: (tuple, float, int, float) -> list
        """
        获取等距离的圆周点-平视\n
        - pos: tuple 位置
        - radius: float 半径
        - n : int 点数量
        """
        posList = []
        for i in xrange(n):
            theta = float(i) / n * 2 * math.pi
            dx = radius * math.cos(theta)
            dz = radius * math.sin(theta)
            posList.append((int(pos[0] + dx), pos[1] + offset, int(pos[2] + dz)))
        return posList

    @staticmethod
    def GetRandomPointFromRing(pos, innerR, outerR, n=1):
        """
        获得圆环内随机点\n
        内半径和外半径相同时即圆周上的点\n
        :param pos: tuple -> 生成位置
        :param innerR: float -> 内半径
        :param outerR: float -> 外半径
        :param n: int -> 生成数量
        :return: list -> 位置列表 [tuple(float, float, float)]
        """
        posList = []
        for _ in xrange(n):
            theta = random.random() * 2 * math.pi
            radius = random.uniform(innerR, outerR)
            dx = radius * math.cos(theta)
            dz = radius * math.sin(theta)
            posList.append((int(pos[0] + dx), pos[1], int(pos[2] + dz)))
        return posList

    @staticmethod
    def GetValueFromRate(rate, left, right):
        """从某区间内根据比例获得值"""
        if rate >= 1:
            return right
        elif rate <= 0:
            return left
        else:
            return float(rate) * (right - left) + left

    @staticmethod
    def GetTupleFromRate(rate, left, right):
        """从某区间内根据比例获得元组"""
        return tuple(map(lambda x, y: Misc.GetValueFromRate(rate, x, y), left, right))

    @staticmethod
    def GetClamp(num, minV, maxV):
        """
        获取在区间的某个数值\n
        若区间外则最大值，区间内则最小值
        """
        assert minV <= maxV
        return min(maxV, max(minV, num))

    @staticmethod
    def GetSetFromLists(*lists):
        """获得不重复的集合\n
        常用于多个怪物列表去重
        """
        resSet = set()
        for element in lists:
            resSet.update(set(element))
        return resSet

    @staticmethod
    def GetRandomFromWeights(weights):
        # type: (list) -> int
        """
        加权随机数\n
        - 例如传入 weight = [1,2,3,4]
        - 返回索引3 -> weight[3] 的 3
        """
        randomValue = random.random() * sum(weights)
        for index, weight in enumerate(weights):
            randomValue -= weight
            if randomValue < 0:
                return index

    @classmethod
    def GetRandomFromWeightDict(cls, config):
        # type: (dict) -> any
        """
        随机权重获得元素\n
        数据格式：{"key1": 10, "key2": 20} -> key1
        """
        element = config.items()
        if not element:
            return None
        target = filter(lambda data: data[1] > 0, element)
        weights = [obj[1] for obj in target]
        index = cls.GetRandomFromWeights(weights)
        return target[index][0]

    @classmethod
    def GetValueInMapRange(cls, value, max_value):
        # type: (int, int) -> int
        """
        获得一个区域对应的值\n
        - 名字还没想好起什么
        - 如:[1, 20]的值对应到[1, 5],当值为10时输出5
        """
        res = value % max_value
        return res if res != 0 else max_value

    @classmethod
    def CreateUUID(cls):
        """创建uuid字段"""
        return str(uuid.uuid4())

    # -----------------------------------------------------------------------------------

    @staticmethod
    def ParseTreeInfo(storage, context, **kwargs):
        # type: (dict, dict, any) -> str
        """解析技能数据显示 - 尚未优化"""
        formula = context.get("formula", {})  # type: dict
        formatDict = {}

        for key, config in formula.iteritems():
            assert isinstance(config, dict)
            paramValue = []
            attrMap = context.get("map", {})  # type: dict
            for paramKey in config.get("param"):
                assert isinstance(paramKey, str)
                attrKey = attrMap.get(paramKey)
                attrValue = storage
                # 遍历索引
                for dataKey in attrKey.split(".")[1:]:
                    match = re.findall("<(.*)>", dataKey)
                    if match:
                        dataKey = match[0]
                        dataKey = kwargs.get(dataKey)
                    attrValue = attrValue.get(dataKey, 0)
                paramValue.append(attrValue)
            # 解析变量值
            parseValue = None
            # 使用特殊方法获得的值
            condition = config.get("condition")  # type: dict
            if not condition:
                # 使用lambda计算的值
                parseValue = config["get"](*paramValue)
            else:
                # 操作方式
                operator = condition.get("operator")
                operateObj = condition.get("data")  # type: dict
                if operator == "range":
                    # 默认使用第一个参数
                    matchTarget = paramValue[0]
                    for onRange, matchOutCome in operateObj.iteritems():
                        if matchTarget in range(*onRange):
                            parseValue = matchOutCome
                            break
            # -----------------------------------------------------------------------------------
            if parseValue is None:
                print "[error]", "错误解析：%s" % key
                return ""
            formatDict[key] = parseValue
            # -----------------------------------------------------------------------------------
        return context["text"].format(**formatDict)

    @classmethod
    def ModifyDataConfig(cls, config, src):
        # type: (dict, dict) -> None
        """属性修正"""
        if "__fix__" in config:
            return

        # print "[suc]", "parsing nums: %d" % len(config)

        def copy_src(src_key):
            # type: (str) -> None
            """数据修正"""
            target = config[src_key]
            # print "[debug]", "copy data: %s" % value
            data = copy.deepcopy(src[target[1:]])  # type: dict
            data.pop("__fix__", None)
            is_skip = data.pop("__skip_parse__", False)
            config[src_key] = data
            if not is_skip:
                cls.ModifyDataConfig(data, src)

        def modify_src(src_key):
            # type: (str) -> None
            """属性修正"""
            # print "[info]", "modify data: %s" % key
            targets = src_key.replace("#", "").split(".")
            if len(targets) <= 1:
                print "[warn]", "Invalid modify value: %s" % src_key
                return
            obj = config
            while targets:
                target_key = targets.pop(0)
                if not targets:
                    # old_value = obj[target_key]
                    obj[target_key] = config.pop(src_key)
                    # print "[info]", "set %s" % old_value, "->", obj[target_key]
                    break
                obj = obj.get(target_key)
                if not obj:
                    print "[error]", "Invalid parse key: %s" % src_key
                    return

        modify_set, parse_set = set(), set()
        for key, value in config.items():
            if isinstance(value, str) and value.startswith("@"):
                parse_set.add(key)
            if key.startswith("#"):
                modify_set.add(key)
        for key in parse_set:
            copy_src(key)
        for key in modify_set:
            modify_src(key)
        config["__fix__"] = True

    @classmethod
    def CleanDictOrList(cls, _data, exKey):
        if isinstance(_data, list):
            removeList = []
            for v in _data:
                if isinstance(v, dict) or isinstance(v, list):
                    cls.CleanDictOrList(v, exKey)
                elif isinstance(v, str) and v == exKey:
                    removeList.append(v)
            for shit in removeList:
                _data.remove(shit)
        elif isinstance(_data, dict):
            if exKey in _data.keys():
                del _data[exKey]
            for v in _data.values():
                if type(v) == dict or type(v) == list:
                    cls.CleanDictOrList(v, exKey)

    @classmethod
    def UnicodeConvert(cls, context):
        if isinstance(context, dict):
            return {cls.UnicodeConvert(key): cls.UnicodeConvert(value) for key, value in context.iteritems()}
        elif isinstance(context, list):
            return [cls.UnicodeConvert(element) for element in context]
        elif isinstance(context, tuple):
            tmp = [cls.UnicodeConvert(element) for element in context]
            return tuple(tmp)
        elif isinstance(context, unicode):
            return context.encode("utf-8")
        else:
            return context

    @classmethod
    def CleanDictByMatch(cls, _data, targetKey):
        if isinstance(_data, dict):
            for key in _data.keys():
                if re.match(targetKey, key):
                    del _data[key]
            for v in _data.values():
                if isinstance(v, dict):
                    cls.CleanDictByMatch(v, targetKey)

    @classmethod
    def ColorConvertRGB(cls, color, small=False):
        """十六进制转换成RGB元组"""
        if color.startswith("#"):
            target = color.replace("#", "")
        else:
            target = color.replace("0x", "")
        target = target.strip()
        length = len(target)
        res = []
        for i in xrange(0, length, 2):
            char = target[i:i + 2]
            data = cls.GetHexConvert(char)
            if small:
                data /= 255.0
            res.append(data)
        return tuple(res)

    @classmethod
    def GetHexConvert(cls, value):
        # type: (str) -> int
        """将十六进制转成十进制"""
        res = 0
        for index in xrange(len(value)):
            char = value[-index + 1]
            if char.isalpha():
                num = cls._hex_map[char.lower()]
            else:
                num = int(char)
            res += num * 16 ** index
        return res

    @staticmethod
    def _GetRotFromPoints2D(fromPos, toPos):
        """
        获得二维两点间的转角\n
        - 网易已给出接口
        """
        deltaV = tuple(p - q for p, q in zip(fromPos, toPos))
        try:
            dy = float(deltaV[2]) / deltaV[0]
            degree = math.degrees(math.atan(dy))
            if toPos[0] < fromPos[0] and toPos[2] > fromPos[2]:
                degree += 180
            elif toPos[0] < fromPos[0] and toPos[2] < fromPos[2]:
                degree += 180
            elif toPos[0] > fromPos[0] and toPos[2] < fromPos[2]:
                degree += 360
            elif deltaV[2] == 0:
                if toPos[0] > fromPos[0]:
                    return 0
                else:
                    return 180
            return degree

        except ZeroDivisionError:
            if toPos[2] > fromPos[2]:
                return 90
            elif toPos[2] < fromPos[2]:
                return 270
            else:
                return None


class Vector(object):
    """向量"""

    def __init__(self, *args):
        self.dim = len(args)
        self.vec = list(args)

    def __len__(self):
        """获得向量维度"""
        return self.dim

    def __neg__(self):
        """取负"""
        self.vec = list(map(lambda x: -x, self.vec))
        return self

    def __pos__(self):
        """取正"""
        return self

    def __add__(self, other):
        """
        向量加法并返回一个新向量\n
        - newVector = Vector1 + Vector2
        - newVector = Vector1 + (1, 2, 3)
        - newVector = Vector1 + [1, 2, 3]
        """
        if self.dim != len(other):
            raise ValueError("要求同纬度向量：%s/%s" % (self.dim, len(other)))
        return self.__class__(*map(lambda x, y: x + y, self.vec, other))

    def __radd__(self, other):
        """
        向量加法并赋值\n
        - Vector1 += Vector2
        - Vector1 += (1, 2, 3)
        - Vector1 += [1, 2, 3]
        """
        if self.dim != len(other):
            print "[error]", "要求同纬度向量：%s/%s" % (self.dim, len(other))
            return
        self.vec = map(lambda x, y: x + y, self.vec, other)

    def __sub__(self, other):
        """
        向量减法并返回一个新向量\n
        - newVector = Vector1 - Vector2
        - newVector = Vector1 - (1, 2, 3)
        - newVector = Vector1 - [1, 2, 3]
        """
        if self.dim != len(other):
            print "[error]", "要求同纬度向量：%s/%s" % (self.dim, len(other))
            return
        if isinstance(other, Vector):
            other = other.vec
        return self.__class__(*map(lambda x, y: x - y, self.vec, other))

    def __rsub__(self, other):
        """
        向量减法并赋值\n
        - Vector1 -= Vector2
        - Vector1 -= (1, 2, 3)
        - Vector1 -= [1, 2, 3]
        """
        if self.dim != len(other):
            print "[error]", "要求同纬度向量：%s/%s" % (self.dim, len(other))
            return
        self.vec = map(lambda x, y: x - y, self.vec, other)

    def __mul__(self, other):
        """
        向量乘法并返回一个新向量\n
        - NewVector = Vector1 * 2
        - NewVector = Vector1 * 2.5
        """
        return self.__class__(*map(lambda x: x * other, self.vec))

    def __rmul__(self, other):
        """
        向量乘法并赋值
        - Vector1 *= 2
        - Vector1 *= 2.5
        """
        self.vec = map(lambda x: x * other, self.vec)

    def __div__(self, other):
        """
        向量除法并返回一个新向量\n
        等比例缩小\n
        - NewVector = Vector1 / 2.5
        """
        other *= 1.0
        return self.__class__(*map(lambda x: x / other, self.vec))

    def __rdiv__(self, other):
        """
        向量除法并赋值\n
        等比例缩小\n
        - Vector1 /= 2.5
        """
        other *= 1.0
        self.vec = map(lambda x: x / other, self.vec)

    def __eq__(self, other):
        """判断向量相等"""
        if self.dim != len(other):
            return False

        return all(map(lambda x, y: x == y, self.vec, other))

    def __ne__(self, other):
        """判断向量不等于"""
        return not self.__eq__(other)

    def __str__(self):
        return "Vector(%s)" % " ".join(str(x) for x in self.vec)

    def __getitem__(self, index):
        """获得向量索引值"""
        if index > self.dim:
            print "[error]", "索引超出向量维度：%s/%s" % (index, self.dim)
            return 0
        return self.vec[index]

    # -----------------------------------------------------------------------------------

    def Dot(self, vector):
        # type: (Vector) -> any
        """
        向量点乘\n
        - 对应位置上的值相乘再相加的操作
        """
        if self.dim != vector.dim:
            print "[error]", "要求同纬度向量：%s/%s" % (self.dim, vector.dim)
            return 0
        return sum(map(lambda x, y: x * y, self.vec, vector.vec))

    def Cross(self, vector):
        # type: (Vector) -> Vector
        """向量叉乘"""

    # -----------------------------------------------------------------------------------

    def Length(self):
        """返回该向量的长度"""
        return math.sqrt(sum(map(lambda x: math.pow(x, 2), self.vec)))

    def LengthSquared(self):
        """返回该向量的长度的平方"""
        return sum(map(lambda x: math.pow(x, 2), self.vec))

    # -----------------------------------------------------------------------------------

    def Normalized(self):
        """
        返回长度为 1 时的该向量。\n
        - 进行标准化时，向量方向保持不变，但其长度为 1.0。\n
        - 请注意，当前向量保持不变，返回一个新的归一化向量。如果 要归一化当前向量，请使用Normalize函数。\n
        - 如果向量太小而无法标准化，则返回零向量。
        """
        length = self.Length()
        newVec = []
        for element in self.vec:
            newVec.append(element / length)
        return self.__class__(newVec)

    def Normalize(self):
        """
        使该向量标准化，向量方向保持不变，但其长度变为 1.0。\n
        - 请注意，该函数无返回值，仅改变当前向量，如果要返回当前向量的标准化值且不改变该向量，请使用Normalized函数。\n
        - 如果向量太小而无法标准化，则设置为零向量。
        """
        length = self.Length()
        newVec = []
        for element in self.vec:
            newVec.append(element / length)
        self.vec = newVec
        return self

    # -----------------------------------------------------------------------------------

    def ToTuple(self):
        # type: () -> tuple
        """返回该向量的元组类型"""
        return tuple(self.vec)

    def ToList(self):
        # type: () -> list
        """返回该向量的列表类型"""
        return list(self.vec)


class Vector2(Vector):
    """二维向量"""

    def __init__(self, *args):
        super(Vector2, self).__init__(*args)
        self.x, = args[0]
        self.y, = args[1]

    def Cross(self, vec):
        # type: (Vector2) -> any
        """二维叉乘是模"""
        return self.x * vec.y - self.y * vec.x


class MVector3(Vector):
    """三维向量"""

    def __init__(self, *args):
        super(MVector3, self).__init__(*args)
        self.x = args[0]
        self.y = args[1]
        self.z = args[2]

    def Cross(self, vec):
        """三维叉乘是向量"""
        return self.y * vec[2] - self.z * vec[1], self.z * vec[0] - self.x * vec[2], self.x * vec[1] - self.y * vec[0]


class Algorithm(object):
    """算法类"""

    @classmethod
    def lerp(cls, start, end, smooth=0.2, error=0.5):
        """比例误差差值"""
        pre = start
        while abs(end - pre) >= error:
            pre += (end - pre) * smooth
            yield round(pre, 2)
        yield end

    @classmethod
    def lerpInt(cls, start, end, smooth=0.2, error=0.5):
        """比例误差整型差值"""
        pre = start
        while abs(end - pre) >= error:
            pre += (end - pre) * smooth
            yield int(math.ceil(pre))
        yield end

    @classmethod
    def lerpValueInTime(cls, start, end, duration=1.0, tick=False):
        """定时单值差值"""
        maxDuration = int((30 * duration) if not tick else duration)
        for i in xrange(maxDuration):
            rate = float(i) / maxDuration
            yield Misc.GetValueFromRate(rate, start, end)
        yield end

    @classmethod
    def lerpTupleInTime(cls, start, end, duration=1.0):
        """定时元组差值"""
        maxDuration = int(30 * duration)
        for i in xrange(maxDuration):
            rate = float(i) / maxDuration
            yield Misc.GetTupleFromRate(rate, start, end)
        yield end

    @classmethod
    def poly(cls, dim, x):
        res = 0
        dimLength = len(dim)
        for i, k in enumerate(dim):
            res += k * math.pow(x, dimLength - i - 1)
        return res

    @classmethod
    def parabola(cls, y, duration=20):
        """抛物线生成"""
        p = y ** 2 / (2.0 * duration)
        sign = 1 if y >= 0 else -1
        for x in xrange(1, y + 1):
            yield sign * (2 * p * x) ** 0.5

    @classmethod
    def parabola_blend_float(cls, y0, y1, duration=20):
        """抛物线过渡"""
        p = (y1 + y0) * (y1 - y0) / (2.0 * duration)
        a = y1 ** 2 - 2 * p * duration
        for x in xrange(1, duration + 1):
            yield (2 * p * x + a) ** 0.5

    @classmethod
    def parabola_blend_int(cls, y0, y1, duration=20):
        """抛物线过渡"""
        p = (y1 + y0) * (y1 - y0) / (2.0 * duration)
        a = y1 ** 2 - 2 * p * duration
        for x in xrange(1, duration + 1):
            yield int((2 * p * x + a) ** 0.5)

    @classmethod
    def map_range(cls, x, min_x, max_x, a, b):
        """区间映射"""
        # assert min_x <= x <= max_x
        return a + (b - a) * (x - min_x) / float(max_x - min_x)


class PIDAlgorithm(object):

    def __init__(self, dt, _max, _min, kp, kd, ki):
        self.dt = dt  # 循环时长
        self.max = _max
        self.min = _min
        self.kp = kp
        self.kd = kd
        self.ki = ki
        self.integral = 0
        self.pre_error = 0

    def calculate(self, point, pv):
        error = point - pv  # 误差
        p_out = self.kp * error  # 比例项
        self.integral += error * self.dt
        i_out = self.ki * self.integral  # 积分项
        derivative = (error - self.pre_error) / self.dt
        d_out = self.kd * derivative  # 微分项

        output = p_out + i_out + d_out  # 新的目标值

        output = max(self.min, min(output, self.max))
        self.pre_error = error  # 保存本次误差
        return output


class Formula(object):
    """计算公式"""
    _config = {}

    @classmethod
    def Register(cls, attrKey, base, formula):
        # type: (str, dict, any) -> None
        """公式注册"""
        config = copy.deepcopy(base)
        config.update({"formula": formula})
        cls._config[attrKey] = config

    @classmethod
    def GetValue(cls, attrKey, param):
        # type: (str, any) -> any
        """获得公式值"""
        config = cls._config.get(attrKey)  # type: dict
        if not config:
            print "[error]", "公式不存在：", attrKey
            return
        return cls._GetValue(config, param)

    @classmethod
    def _GetValue(cls, config, param):
        # type: (dict, any) -> any
        """获得下级最大经验"""
        value = config.get(param)
        if not value:
            last_value = cls._GetValue(config, param - 1)
            formula = config.get("formula")
            value = formula(last_value, param)
            config[param] = value
        return value


class Eval(object):
    """复刻内置函数计算部分"""

    @classmethod
    def Run(cls, formula):
        """执行计算"""
        return float(cls.CalBrace(formula.replace(" ", "")))

    @classmethod
    def ModifySign(cls, formula):
        # type: (str) -> str
        """修正符号"""
        return re.sub(r"-\+|\+-", "-", formula).replace("--", "+").replace("**+", "**").replace("++", "+").strip("+")

    @classmethod
    def CalBrace(cls, formula):
        """计算括号内容"""
        while True:
            brace = re.search(r"\([^()]*\)", formula)
            if not brace:
                break
            brace = brace.group()
            warp = cls.CalBrace(brace.strip("()"))
            # print "[debug]", "warp, brace -> ", warp, brace
            # print "=" * 50
            formula = formula.replace(brace, warp)
        return cls.CalBaseRule(formula)

    @classmethod
    def CalBaseRule(cls, formula):
        """根据四则运算计算结果"""
        while re.findall(r"[*/+-]", formula):
            formula = cls.ModifySign(formula)
            # print "[suc] CalBaseRule:", formula
            multiTime = re.search(r"([-|+]?\d*\.?\d+\*{2}[-|+]?\d*\.?\d+)", formula)
            if multiTime:
                target = multiTime.group()
                val = re.split(r"\*{2}", target)
                value = "+%s" % float(val[0]) ** float(val[-1])
                formula = formula.replace(target, value)
                continue
            multiTime = re.search(r"([-|+]?\d*\.?\d+[*/]+[-|+]?\d*\.?\d+)", formula)
            if multiTime:
                target = multiTime.group()
                value = cls.CalMutDiv(target)
                formula = formula.replace(target, value)
                continue
            formula = cls.CalAddSub(formula)
            break
        return cls.ModifySign(formula)

    @classmethod
    def CalMutDiv(cls, formula):
        """计算乘除内容"""
        val = re.split(r"/{2}", formula)
        if len(val) >= 2:
            result = str(float(val[0]) // float(val[-1]))
            return "+%s" % result
        val = re.split(r"\*", formula)
        if len(val) >= 2:
            result = str(float(val[0]) * float(val[-1]))
            return "+%s" % result
        else:
            val = re.split(r"/", formula)
            result = str(float(val[0]) / float(val[-1]))
            return "+%s" % result

    @classmethod
    def CalAddSub(cls, formula):
        """计算加减内容"""
        ret = re.findall(r"-?\d*\.?\d+", formula)
        result = 0
        for i in ret:
            result += float(i)
        # print "[suc] CalAddSub", "%s = %s" % (formula, result)
        return "+%s" % result


class JsonTool(object):
    """Json工具方法"""

    @classmethod
    def UnicodeConvert(cls, context):
        if isinstance(context, dict):
            return {cls.UnicodeConvert(key): cls.UnicodeConvert(value) for key, value in context.iteritems()}
        elif isinstance(context, list):
            return [cls.UnicodeConvert(element) for element in context]
        elif isinstance(context, tuple):
            tmp = [cls.UnicodeConvert(element) for element in context]
            return tuple(tmp)
        elif isinstance(context, unicode):
            return context.encode("utf-8")
        else:
            return context

    @classmethod
    def Load(cls, f, encode="utf-8"):
        """解析Json文件"""
        context = json.load(f, encoding=encode)  # type: dict
        return cls.UnicodeConvert(context)

    @classmethod
    def LoadPath(cls, path):
        # type: (str) -> dict
        """解析路径的Json"""
        with open(path, "r") as f:
            return cls.Load(f)

    @classmethod
    def LoadStr(cls, context):
        """以字符串形式读成字典"""
        context = json.loads(context)
        return cls.UnicodeConvert(context)

    @classmethod
    def LoadStripComment(cls, f):
        contextList = []
        for line in f.readlines():
            if re.findall("//.*", line):
                line = re.sub("//.*", "", line)
            contextList.append(line)
        return cls.LoadStr("\n".join(contextList))

    @staticmethod
    def Save(content, f):
        """保存Json文件"""
        json.dump(content, f, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)


if __name__ == '__main__':
    """测试"""
    print Misc.ColorConvertRGB("#FFFF00", True)
    # pid = PidAlgorithm(0.1, 100, -100, 0.1, 0.01, 0.5)
    # target = 30
    # val = target
    # z = []
    # for i in xrange(60):
    #     inc = pid.calculate(0, val)
    #     val += inc
    #     print target - val

    # print list(Algorithm.parabola_blend(100, 200, 10))
    # print Algorithm.map_range(0.5, 0, 1, 0, 4)
    # print Algorithm.map_range(90, 1, 100, 5, 15)
