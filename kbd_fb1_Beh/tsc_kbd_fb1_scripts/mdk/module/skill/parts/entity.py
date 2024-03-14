# -*- coding:utf-8 -*-


import copy
import math
import random

import mod.server.extraServerApi as serverApi

from ..const import ModuleSkill
from ....common.system.base import GameEntity
from ....common.utils.misc import Misc
from ....loader import MDKConfig
from ....server.entity import *


class SkillConfigEntity(LivingEntity):
    """配置技能实体"""
    __mVersion__ = 9
    _skill_type_map = {
        "direct_attack": "ParseDirectAttack",
        "direct_effect": "ParseDirectEffect",
        "range_attack": "ParseRangeAttack",
        "projectile_attack": "ParseProjectileAttack",
        "duration_attack": "ParseDurationAttack",
        "timeline": "ParseTimeline",
        "direct_move": "ParseMoveUnit",
        "move_control": "ParseMoveControl",
        "netease_particle": "ParseNeteaseParticle",
        "explosion": "ParseExplosion"
    }

    def __init__(self, entityId):
        super(SkillConfigEntity, self).__init__(entityId)
        self.system = MDKConfig.GetModuleServer()  # type: MDKConfig.GetModuleServerSystemCls()
        self.position_cache = {}
        self.generator = []
        self.detector_entity = []
        self.particle_entity = []

    def __del__(self):
        # print "[info]", "del:%s" % self.__class__.__name__
        pass

    # -----------------------------------------------------------------------------------

    def ParseSkillConfig(self, config, context=None):
        """解析技能配置"""
        skill_type = config["type"]
        func = self._skill_type_map.get(skill_type)
        if not func:
            print "[error]", "Invalid skill type: %s" % skill_type
            return lambda _: None
        Misc.ModifyDataConfig(config, ModuleSkill.SkillData)
        trigger = getattr(self, func)(config)
        return lambda args=context: trigger(args)

    def StartCoroutine(self, func, recall=None):
        """开启协程"""
        generator = self.system.StartCoroutine(func, recall)
        self.generator.append(generator)

    def StartCoroutineLine(self, config):
        """开启协程线"""
        generator = self.system.StartCoroutineLine(config)
        self.generator.append(generator)

    # -----------------------------------------------------------------------------------

    def Discard(self):
        """销毁技能"""
        for config in self.generator:
            if isinstance(config, list):
                for generator in config:
                    self.system.StopCoroutine(generator)
                continue
            self.system.StopCoroutine(config)
        for entity_id in self.detector_entity:
            self.system.DestroyEntity(entity_id)
        self.generator = []

    def DiscardParticle(self):
        """销毁技能生成的特效"""
        for entity_id in self.particle_entity:
            self.system.DestroyEntity(entity_id)

    # -----------------------------------------------------------------------------------

    def ParseDirectAttack(self, config):
        """解析直接攻击"""
        effect = config["effect"]
        if effect:
            effect = self.ParseDirectEffect(effect)
        # -----------------------------------------------------------------------------------
        particle = config["particle"]
        if particle:
            particle = self.ParseNeteaseParticle(particle)

        def active(args):
            victim_id = args["victim_id"]
            delay = self.GetTargetValue("delay", config, args)
            if effect:
                effect(args)
            fire = config["fire"]
            if fire:
                self.SetEntityFire(victim_id, **fire)
            if particle:
                particle(args)
            move = config["move"]
            if move:
                trigger = self.ParseMoveUnit(move)
                trigger(args)
            if delay:
                yield int(delay * 30)
            damage = self.GetTargetValue("damage", config, args)
            self.SetInstantDamage(victim_id, damage, **config)
            yield 0

        return lambda context: self.StartCoroutine(active(context))

    def ParseDirectEffect(self, config):
        """解析直接效果"""

        def active(args):
            target = self.GetTargetId(config["target"], args)
            self.CastEffect(target, **config)

        return lambda context: active(context)

    def ParseRangeAttack(self, config):
        """
        解析范围伤害\n
        - delay: float
        - damage: dict
        - detector: dict
        - particle: dict
        """
        damage = self.ParseDirectAttack(config["damage"])
        detect = self.ParseDetector(config["detector"])
        particle = config["particle"]
        if particle:
            particle = self.ParseNeteaseParticle(particle)

        def active(args):
            delay = self.GetTargetValue("delay", config, args)
            if delay:
                yield int(delay * 30)
            for victim_id in detect(args):
                args["victim_id"] = victim_id
                damage(args)
            if particle:
                particle(args)
            yield 0

        return lambda context: self.StartCoroutine(active(context))

    def ParseProjectileAttack(self, config):
        """
        解析抛射物攻击\n
        - projectile: dict
        """
        data = config["projectile"]  # type: dict
        trigger = self.ParseProjectile(data)
        # -----------------------------------------------------------------------------------
        on_hit = data["on_hit"]
        if on_hit:
            on_hit = self.ParseSkillConfig(on_hit)
        # -----------------------------------------------------------------------------------
        on_hit_entity = data["on_hit_entity"]
        if on_hit_entity:
            on_hit_entity = self.ParseSkillConfig(on_hit_entity)
        # -----------------------------------------------------------------------------------
        on_hit_block = data["on_hit_block"]
        if on_hit_block:
            on_hit_block = self.ParseSkillConfig(on_hit_block)
        # -----------------------------------------------------------------------------------
        on_fly = data["on_fly"]
        if on_fly:
            on_fly = self.ParseSkillConfig(on_fly)
        # -----------------------------------------------------------------------------------
        netease_particle = data["netease_particle"]
        if netease_particle:
            netease_particle = self.ParseNeteaseParticle(netease_particle)

        def active(args):
            if not self.IsAlive():
                return
            projectile = trigger(args)
            args["projectile_id"] = projectile.id
            if any([on_hit, on_hit_entity, on_hit_block]):
                projectile.dataDict = {
                    "on_hit": on_hit,
                    "on_hit_entity": on_hit_entity,
                    "on_hit_block": on_hit_block,
                    "context": args
                }
                projectile.ConfigHitRecall(self._RecallOnProjectileHit)
            if on_fly:
                projectile.dataTemp = on_fly(args)
            if netease_particle:
                # 抛射物特效
                netease_particle(args)

        def warped(args):
            function = config["function"]
            if not function:
                active(args)
                yield 0
                return
            # todo: 函数修正 兼容配置写法
            target = function["target"]
            target_key = "__%s__" % target
            delay = self.GetTargetValue("delay", function, args)
            interval = self.GetTargetValue("interval", function, args)
            iterable = self.GetTargetValue("iterable", function, args)
            if delay:
                yield int(delay * 30)
            if not interval:
                for _data in iterable():
                    args[target_key] = _data
                    active(args)
                yield 0
            else:
                for _data in iterable():
                    args[target_key] = _data
                    active(args)
                    yield interval

        return lambda context: self.StartCoroutine(warped(context))

    def ParseProjectile(self, config):
        """
        解析抛射物\n
        - __direction__: 上下文修正方向
        """

        def active(args):
            param = copy.deepcopy(config)  # type: dict
            engine_type = param["engine_type"]
            damage = param["damage"]
            if isinstance(damage, list):
                param["damage"] = random.randint(*damage)
            elif isinstance(damage, str):
                param["damage"] = self.GetTargetValue("damage", param, args)
            param["gravity"] = self.GetTargetValue("gravity", param, args)
            position = param["position"]
            if isinstance(position, dict):
                offset = self.GetTargetValue("offset", position, args)
                param["position"] = RawEntity.GetModifyPos(self.id, offset)
            else:
                param["position"] = RawEntity.GetPos(self.id)
            if "__direction__" in args:
                param["direction"] = args["__direction__"]
            else:
                direction = param["direction"]
                if not isinstance(direction, tuple):
                    param["direction"] = self.GetDrt(param["horizon"])
            target_id = config["track_target"]
            if target_id:
                target_id = self.GetTargetValue("track_target", config, args)
                if self.game_comp.IsEntityAlive(target_id):
                    param["targetId"] = target_id
            return ProjectileEntity.CreateProjectile(engine_type, self.id, param)

        return lambda context: active(context)

    def ParseDurationAttack(self, config):
        """
        解析抛射物攻击\n
        - delay: float
        - damage: dict
        - detector: dict
        - duration: float
        - interval: float
        - damage_once: bool
        """
        interval = config["interval"]
        damage = self.ParseDirectAttack(config["damage"])
        detect = self.ParseDetector(config["detector"])

        interval_tick = int(30 * interval)
        if config["damage_once"]:
            def damage_once(args):
                duration = self.GetTargetValue("duration", config, args)
                impact_time = int(float(duration) / interval)
                yield int(config["delay"] * 30)
                damage_set = set()
                for _ in xrange(impact_time):
                    for victim_id in detect(args):
                        if victim_id in damage_set:
                            continue
                        damage_set.add(victim_id)
                        args["victim_id"] = victim_id
                        damage(args)
                    yield interval_tick
                del damage_set

            return lambda context: self.StartCoroutine(damage_once(context))
        else:
            def multi_damage(args):
                duration = self.GetTargetValue("duration", config, args)
                impact_time = int(float(duration) / interval)
                yield int(config["delay"] * 30)
                for _ in xrange(impact_time):
                    for victim_id in detect(args):
                        args["victim_id"] = victim_id
                        damage(args)
                    yield interval_tick

            return lambda context: self.StartCoroutine(multi_damage(context))

    def ParseTimeline(self, config):
        """
        解析时间线\n
        - timeline: dict
        """
        timeline = config["timeline"]  # type: dict

        def active(args):
            builder = {}

            def build_task(target):
                """构造任务"""
                data = ModuleSkill.SkillData[target[1:]]
                Misc.ModifyDataConfig(data, ModuleSkill.SkillData)
                return self.ParseSkillConfig(data, args)

            for sec, tasks in timeline.items():
                if isinstance(tasks, str):
                    # print "[suc]", "parsing task: %s" % tasks
                    builder[float(sec)] = [build_task(tasks)]
                elif isinstance(tasks, list):
                    task_list = []
                    for index, task in enumerate(tasks):
                        # print "[suc]", "parsing task: %s" % task
                        """支持字典修正[已废弃]- 额外缓存开销和不利于后续复用"""
                        # if isinstance(task, dict):
                        #     key = task.pop("line")  # type: str
                        #     src_data = ModuleSkill.SkillData[key[1:]]
                        #     self.ModifyDataConfig(src_data)
                        #     task.update(src_data)
                        #     task.pop("__fix__", None)
                        #     self.ModifyDataConfig(task)
                        #     # create new cache
                        #     uid = Misc.CreateUUID()
                        #     key = "@%s" % uid
                        #     ModuleSkill.SkillData[uid] = {"__skill_cache__": True, "data": task}
                        #     # replace src data
                        #     tasks[index] = key
                        #     task_list.append(self.ParseSkillConfig(task, args))
                        # else:
                        new_task = ModuleSkill.SkillData[task[1:]]
                        # if "__skill_cache__" in data:
                        #     task_list.append(self.ParseSkillConfig(data["data"], args))
                        #     continue
                        Misc.ModifyDataConfig(new_task, ModuleSkill.SkillData)
                        task_list.append(self.ParseSkillConfig(new_task, args))
                    builder[float(sec)] = task_list
            self.StartCoroutineLine(builder)

        return lambda context: active(context)

    def ParseMoveControl(self, config):
        """
        解析运动控制\n
        - controls: list
        - delay: float
        """
        controls = config["controls"]  # type: list

        def active(args):
            delay = self.GetTargetValue("delay", config, args)
            yield int(delay * 30)
            if not self.IsAlive():
                return

            def build_task(target, _index):
                """构造任务"""
                # print "[suc]", "parsing move: %s" % target
                """支持字典修正[已废弃]- 额外缓存开销和不利于后续复用"""
                # if isinstance(target, dict):
                #     key = target["control"]  # type: str
                #     new_task = copy.deepcopy(ModuleSkill.SkillData[key[1:]])  # type: dict
                #     new_task.update(target)
                #     new_task.pop("__fix__", None)
                #     self.ModifyDataConfig(new_task)
                # else:
                new_task = ModuleSkill.SkillData[target[1:]]
                Misc.ModifyDataConfig(new_task, ModuleSkill.SkillData)
                return self.ParseMoveUnit(new_task)

            for index, control in enumerate(controls):
                trigger = build_task(control, index)
                trigger(args)

        return lambda context: self.StartCoroutine(active(context))

    def ParseNeteaseParticle(self, config):
        """
        解析网易特效\n
        - path: str
        - model: str
        - name: str
        """
        path = config["path"]
        model = config["model"]
        name = config["name"]

        def active(args):
            target = self.GetTargetValue("target", config, args)
            duration = self.GetTargetValue("duration", config, args)
            pos = self.GetTargetPosition(config, args)
            if isinstance(target, str):
                particle = ParticleEntity(target)
            else:
                track = self.GetTargetValue("track", config, args)
                binder = self.GetTargetValue("binder", config, args)
                rot = RawEntity.GetRot(binder)
                if not rot:
                    rot = self.GetRot()
                particle = self.AddParticleEntity(GameEntity.detector, pos=pos, rot=rot)
                particle.SetBinder(binder)
                if track:
                    track_offset = config.get("track_position")
                    offset = self.GetTargetValue("offset", track_offset, args)
                    forward = offset[2]
                    particle.SetTrackEntity(track, True, forward, lifeTime=int(duration * 30))
            # -----------------------------------------------------------------------------------
            particle.SetModel(model)
            particle.SetFixBind(path, name)
            particle.Play()
            particle.Destroy(duration)
            self.particle_entity.append(particle.id)
            return particle

        return lambda context: active(context)

    def ParseExplosion(self, config):
        """
        解析爆炸\n
        - position: dict
        - radius: int
        - fire: bool
        - breaks: bool
        """
        radius = config["radius"]
        fire = config["fire"]
        breaks = config["breaks"]

        def active(args):
            pos = self.GetTargetPosition(config, args)
            self.system.AddExplosion(pos, radius, fire=fire, breaks=breaks)

        return lambda context: active(context)

    # -----------------------------------------------------------------------------------

    def _RecallOnProjectileHit(self, projectile):
        # type: (ProjectileEntity) -> None
        """抛射物碰撞回调"""
        config = projectile.dataDict
        on_hit = config["on_hit"]
        on_hit_entity = config["on_hit_entity"]
        on_hit_block = config["on_hit_block"]
        context = config["context"]
        context["projectile_hit_pos"] = projectile.GetHitPos()
        if projectile.hitType == "ENTITY" and on_hit_entity:
            context["victim_id"] = projectile.hitTarget
            on_hit_entity(context)
        elif projectile.hitType == "BLOCK" and on_hit_block:
            on_hit_block(context)
        if on_hit:
            on_hit(context)
        if projectile.IsDestroyOnHit() and projectile.dataTemp:
            if not isinstance(projectile.dataTemp, list):
                self.system.StopCoroutine(projectile.dataTemp)
                return
            for generator in projectile.dataTemp:
                self.system.StopCoroutine(generator)

    # -----------------------------------------------------------------------------------

    def ParseDetector(self, config):
        """
        解析检测体\n
        - radius: int
        - filters: dict
        - positions: dict
        """
        uid = Misc.CreateUUID()

        def active(args):
            if not self.IsAlive():
                return []
            spawn_pos = self.GetTargetPosition(config, args, uid=uid)
            args["detector_pos"] = spawn_pos
            args["detector_drt"] = self.drt
            radius = self.GetTargetValue("radius", config, args)
            return self.GetMobAtPos(spawn_pos, radius, [self.GetTameOwner()], **config)

        return lambda context: active(context)

    def ParseMoveUnit(self, config):
        """解析运动任务"""
        action = config["action"]
        if action == "rotation":
            return self.ParseRotationMove(config)
        elif action == "knock":
            return self.ParseKnockMove(config)
        else:
            print "[error]", "action: %s" % action

    def ParseRotationMove(self, config):
        """解析旋转运动"""
        duration = config["duration"]
        # angle = config["angle"]
        follow = config["follow"]  # type: str
        facing = config["facing"]  # type: str

        def facing_rot(args):
            # type: (dict) -> None
            """面向旋转"""
            key = facing.split(".")[-1]
            target = args.get(key)
            if not target:
                # print "[warn]", "Invalid context key: %s" % facing
                return

            def facing_gen():
                delay = self.GetTargetValue("delay", config, args)
                if delay:
                    yield int(delay * 30)
                runtime = int(duration * 30)
                if not runtime:
                    self.SetFacingEntity(target)
                    yield 0
                    return
                for _ in xrange(runtime):
                    suc = self.SetFacingEntity(target)
                    if not suc:
                        yield 0
                        return
                    yield 1

            return self.StartCoroutine(facing_gen)

        def follow_rot(args):
            # type: (dict) -> None
            """跟随旋转"""
            key = follow.split(".")[-1]
            target = args.get(key)
            if not target:
                # print "[warn]", "Invalid context key: %s" % follow
                return

            def follow_gen():
                delay = self.GetTargetValue("delay", config, args)
                if delay:
                    yield int(delay * 30)
                runtime = int(duration * 30)
                if not runtime:
                    rot = RawEntity.GetRot(target)
                    if rot:
                        self.SetRot(rot)
                    yield 0
                    return
                for _ in xrange(runtime):
                    rot = RawEntity.GetRot(target)
                    if not rot:
                        yield 0
                        return
                    self.SetRot(rot)
                    yield 1

            return self.StartCoroutine(follow_gen)

        def rotation_move(args):
            # type: (dict) -> None
            if facing.startswith("context."):
                return facing_rot(args)
            elif follow.startswith("context."):
                return follow_rot(args)

        return rotation_move

    def ParseKnockMove(self, config):
        """解析位移运动"""

        def knock_move(args):
            interval = config["interval"]  # type: int
            direction = config["direction"]
            target_id = self.GetTargetId(config["target"], args)
            if not target_id:
                yield 0
                return
            delay = self.GetTargetValue("delay", config, args)
            if delay:
                yield int(delay * 30)
            action_comp = self.comp_factory.CreateAction(target_id)
            gravity_comp = self.comp_factory.CreateGravity(self.id)

            gravity = self.GetTargetValue("gravity", config, args)
            power = self.GetTargetValue("power", config, args)
            duration = self.GetTargetValue("duration", config, args)
            height = self.GetTargetValue("height", config, args)
            height_max = self.GetTargetValue("height_max", config, args)

            runtime = max(int(duration * 30), 1)

            gravity_gen = None
            if gravity:
                def gravity_effect():
                    gravity_comp.SetGravity(gravity)
                    for _ in xrange(runtime):
                        yield interval

                def clear_effect():
                    if self.IsAlive():
                        gravity_comp.SetGravity(0)

                gravity_gen = self.StartCoroutine(gravity_effect, clear_effect)

            if not direction:  # 垂直方向
                for _ in xrange(runtime):
                    action_comp.SetMobKnockback(0, 0, 0, height, height_max)
                    yield interval
                if gravity_gen:
                    self.system.StopCoroutine(gravity_gen, True)
                return

            abs_angle = direction["abs_angle"]  # type: list

            if abs_angle:  # 绝对角度
                abs_angle = self.GetTargetValue("abs_angle", direction, args)
                for _ in xrange(runtime):
                    action_comp.SetMobKnockback(abs_angle[0], abs_angle[2], power, height, height_max)
                    yield interval
                if gravity_gen:
                    self.system.StopCoroutine(gravity_gen, True)
                return

            facing = direction["facing"]
            horizon, offset = direction["horizon"], direction["offset"]
            if offset:
                horizon = False
            # 基于此目标的旋转修正
            base_target = self.GetTargetId(direction["target"], args)
            if not facing:
                for _ in xrange(runtime):
                    rot = RawEntity.GetEntityRotModify(base_target, horizon, *offset)
                    if not rot:
                        yield 0
                        return
                    drt_x, _, drt_z = serverApi.GetDirFromRot(rot)
                    action_comp.SetMobKnockback(drt_x, drt_z, power, height, height_max)
                    yield interval
                if gravity_gen:
                    self.system.StopCoroutine(gravity_gen, True)
            else:
                facing_target = self.GetTargetId(facing, args)

                def update_direction():
                    if isinstance(facing_target, tuple):
                        face_rot = RawEntity.GetFacingPosVec(target_id, facing_target)
                    else:
                        if not self.game_comp.IsEntityAlive(facing_target):
                            return 0, 0
                        face_rot = RawEntity.GetFacingEntityVec(target_id, facing_target)
                    modify_rot = serverApi.GetRotFromDir(face_rot)
                    x, _, z = serverApi.GetDirFromRot(Misc.GetRotModify(modify_rot, *offset))
                    return x, z

                for _ in xrange(runtime):
                    drt_x, drt_z = update_direction()
                    action_comp.SetMobKnockback(drt_x, drt_z, power, height, height_max)
                    yield interval
                if gravity_gen:
                    self.system.StopCoroutine(gravity_gen, True)

        return lambda context: self.StartCoroutine(knock_move(context))

    def ParseFunction(self, config):
        """解析函数"""
        function_type = config["type"]
        _range = config["range"]
        step = config["step"]
        if function_type == "xrange":
            def active(args):
                start = int(self.GetTargetValue("start", config, args))
                for i in xrange(start, start + _range, step):
                    yield i

            return lambda context: active(context)

    @classmethod
    def GetTargetValue(cls, key, config, context):
        # type: (str, dict, dict) -> any
        """获得目标数据"""
        value = config[key]
        if isinstance(value, str) and value.startswith("context"):
            key = value.split(".")[-1]
            return context.get(key)
        return value

    def GetTargetId(self, target, context):
        # type: (str, dict) -> str
        """
        获得目标Id\n
        - self: str
        - context: str
        """
        if target.startswith("context"):
            key = target.split(".")[-1]
            return context.get(key)
        return self.id

    def GetTargetPosition(self, config, context, key="position", **kwargs):
        """
        获得目标位置修正\n
        - target: str
        - offset: list
        """
        data = config[key]  # type: dict
        offset = self.GetTargetValue("offset", data, context)
        target = self.GetTargetId(data["target"], context)
        if isinstance(target, tuple):
            return Misc.GetPosModify(target, offset)  # 方块类型 -> 绝对偏移
        if data["target"] == "stable":
            uid = kwargs["uid"]
            pos = self.position_cache.get(uid)
            if pos:
                return pos
            else:
                pos = RawEntity.GetModifyPos(target, offset)
                self.position_cache[uid] = pos
                return pos
        return RawEntity.GetModifyPos(target, offset)  # 生物类型 -> 相对偏移

    # -----------------------------------------------------------------------------------

    def SetInstantDamage(self, victimId, value, **kwargs):
        """对实体造成瞬间伤害"""
        if value == 0:
            return
        if not self.game_comp.IsEntityAlive(victimId):
            return
        damage = max(math.trunc(value), 1)
        cause = kwargs["cause"]
        knocked = kwargs["knocked"]

        self.game_comp.SetHurtCD(0)
        self.comp_factory.CreateHurt(victimId).Hurt(damage, cause, self.id, knocked=knocked)
        self.game_comp.SetHurtCD(10)

    def CastEffect(self, victimId, effect, duration=10, level=0, hide=False, **kwargs):
        """释放药水效果"""
        effectComp = self.comp_factory.CreateEffect(victimId)
        return effectComp.AddEffectToEntity(effect, duration, level, not hide)

    def GetMobInRadius(self, _radius, **kwargs):
        """
        获取一定半径的生物\n
        - radius: int
        - filters: dict
        """
        filters = kwargs["filters"]

        detector = kwargs.get("detector", self.id)
        ban_list = kwargs.get("ban_list", [self.id])
        res_list = self.game_comp.GetEntitiesAround(detector, _radius, filters)
        if ban_list:
            res_set = set(res_list)
            res_set.difference_update(set(ban_list))
            return list(res_set)
        return res_list

    def GetMobAtPos(self, pos, _radius, ban_list=None, **kwargs):
        """获取某点的半径生物"""
        detector_id = RawEntity.CreateRaw(GameEntity.detector, pos, self.dim, self.rot)
        res_list = self.GetMobInRadius(_radius, detector=detector_id, **kwargs)
        if not ban_list:
            ban_list = [self.id]
        ban_list.append(detector_id)
        res_set = set(res_list)
        res_set.difference_update(set(ban_list))
        self.system.DestroyEntity(detector_id)
        return list(res_set)
