# -*- coding:utf-8 -*-
import time


class ModEnum(object):
    """模组枚举"""
    # 模组名称
    MOD_IDENTIFIER = "tsc_kbd_fb1"
    # 模组路径
    SCRIPT_DIR = "tsc_kbd_fb1_scripts"


class ModItem(object):
    """模组物品"""


class ModBlock(object):
    """模组方块"""


class ModEntity(object):
    """模组生物"""


class ModTag(object):
    """模组标签"""


class ModFilter(object):
    """模组过滤器"""


class ModEffect(object):
    """模组自定义效果"""


class ModAttr(object):
    """模组自定义属性"""
    skill1 = "skill1"
    skill2 = "skill2"
    skill3 = "skill3"


class ModFog(object):
    """模组迷雾配置"""


class ModMolang(object):
    """模组使用Molang值"""
    skill = "query.mod.skill"

    AllMolang = [
        skill
    ]


class ModDimension(object):
    """模组维度配置"""


# -----------------------------------------------------------------------------------

class ModServer(object):
    """模组服务端配置"""


class ModClient(object):
    """模组客户端配置"""


class ModUI(object):
    """模组UI配置"""


Fog_Man_EntityAttrConfig = {
    "zdkj:fog_man": {
        "attack_cd": 30,
        "attr": "physical"
    }
}

# 出生特效
MobEffectDict = {
}


def CheckBeforeTime(time_str):
    '''检查是否处于某个日期之前'''
    ProcessTime = time_str.split(" ")[0].split("-") + time_str.split(" ")[1].split(":")
    NowTime = time.localtime()
    NowTime = [NowTime.tm_year, NowTime.tm_mon, NowTime.tm_mday, NowTime.tm_hour, NowTime.tm_min, NowTime.tm_sec]
    for i in range(6):
        if int(NowTime[i]) > int(ProcessTime[i]):
            return False
        elif int(NowTime[i]) < int(ProcessTime[i]):
            return True


def PublishTime():
    return "2024-3-9 10:00:00"


BeforeTime = CheckBeforeTime(PublishTime())
print("[debug]BeforeTime", BeforeTime)


