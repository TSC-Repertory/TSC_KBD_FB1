# -*- coding:utf-8 -*-



class CoroutineMgr(object):
    """
    协程运行程序\n
    =====================================\n
    需要放置Tick函数才起效\n
    CoroutineMgr.Tick()放置在<Update>函数里\n
    =====================================\n
    - 传入任务函数:\n
    需要返回一个生成器\n
    CoroutineMgr.StartCoroutine(func)\n
    =====================================\n
    - 延迟顺序执行:\n
    yield <int> 正整数\n
    延迟时间由CoroutineMgr.Tick()放置位置确定\n
    =====================================\n

    - example：
    def func():
        yield 20  # 延迟<20tick>执行task1\n
        print "task1"\n
        yield 5  # 继续延迟<5tick>执行task2\n
        print "task2"\n

    def callback():
        print "callback"

    CoroutineMgr.StartCoroutine(func, callback)
    """
    __mVersion__ = 3

    coroutines = {}
    add_coroutines = {}
    recall_dict = {}

    @classmethod
    def StartCoroutine(cls, func, recall=None):
        """开启协程"""
        coroutine = func if not callable(func) else func()
        cls.add_coroutines[coroutine] = coroutine.next()
        if recall:
            cls.recall_dict[coroutine] = recall
        return coroutine

    @classmethod
    def StopCoroutine(cls, coroutine, isSafe=False):
        """关闭协程"""
        if coroutine not in cls.coroutines:
            return
        del cls.coroutines[coroutine]
        recall = cls.recall_dict.pop(coroutine, None)
        if isSafe and callable(recall):
            recall()

    @classmethod
    def Tick(cls):
        if cls.add_coroutines:
            for coroutine, value in cls.add_coroutines.iteritems():
                cls.coroutines[coroutine] = value
            cls.add_coroutines.clear()

        ended = []
        for coroutine, value in cls.coroutines.items():
            if value > 0:
                value -= 1
                cls.coroutines[coroutine] = value
            if value <= 0 or not value:
                try:
                    new_value = coroutine.next()
                    cls.coroutines[coroutine] = new_value
                except StopIteration:
                    ended.append(coroutine)
        for coroutine in ended:
            cls.StopCoroutine(coroutine, True)

    @classmethod
    def Get(cls, coroutine):
        """获得协程当前yield值"""
        return cls.coroutines.get(coroutine)

    @classmethod
    def StartCoroutineLine(cls, config):
        """创建协程流"""

        storage = []

        def active():
            yield 0
            tick = 0
            for sec in sorted(config):
                pre_tick = int(sec * 30)
                for _ in xrange(pre_tick - tick):
                    yield 1
                tick = pre_tick
                gen_list = config.get(sec, [])  # type: list
                if not gen_list:
                    continue
                for gen in gen_list:
                    if callable(gen):
                        gen()
                    else:
                        storage.append(cls.StartCoroutine(gen))

        _gen = cls.StartCoroutine(active)
        storage.append(_gen)
        return storage


class GameTickCoroutine(CoroutineMgr):
    """游戏帧协程"""
    __mVersion__ = 3

    coroutines = {}
    add_coroutines = {}
    recall_dict = {}

    @classmethod
    def StartCoroutine(cls, func, recall=None):
        return super(GameTickCoroutine, cls).StartCoroutine(func, recall)

    @classmethod
    def StopCoroutine(cls, coroutine, isSafe=False):
        super(GameTickCoroutine, cls).StopCoroutine(coroutine, isSafe)

    @classmethod
    def Tick(cls):
        super(GameTickCoroutine, cls).Tick()

    @classmethod
    def Get(cls, coroutine):
        return super(GameTickCoroutine, cls).Get(coroutine)

    @classmethod
    def StartCoroutineLine(cls, config):
        return super(GameTickCoroutine, cls).StartCoroutineLine(config)
