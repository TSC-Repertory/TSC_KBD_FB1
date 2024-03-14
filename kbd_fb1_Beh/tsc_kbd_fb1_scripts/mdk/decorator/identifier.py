# -*- coding:utf-8 -*-


from functools import wraps


def check_player_id(func):
    """检测使用playerId标识的事件"""

    @wraps(func)
    def warped(*args, **kwargs):
        entity, data = args
        if data["playerId"] != entity.id:
            return
        func(*args, **kwargs)

    return warped


def check_entity_id(func):
    """检测使用entityId标识的事件"""

    @wraps(func)
    def warped(*args, **kwargs):
        entity, data = args
        if data["entityId"] != entity.id:
            return
        func(*args, **kwargs)

    return warped


def check_target_id(func):
    """检测使用targetId标识的事件"""

    @wraps(func)
    def warped(*args, **kwargs):
        entity, data = args
        if data["targetId"] != entity.id:
            return
        func(*args, **kwargs)

    return warped


def check_id(func):
    """检测使用id标识的事件"""

    @wraps(func)
    def warped(*args, **kwargs):
        entity, data = args
        if data["id"] != entity.id:
            return
        func(*args, **kwargs)

    return warped


def check_alive(func):
    """检测自身是否存活"""

    @wraps(func)
    def warped(*args, **kwargs):
        entity = args[0]
        if not entity.IsAlive():
            return
        func(*args, **kwargs)

    return warped
