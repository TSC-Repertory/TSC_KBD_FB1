# -*- coding:utf-8 -*-


from ...client.entity import RawEntity
from const import *
from parser import RenderParser
from ..system.base import *


class RenderModuleClient(ModuleClientBase):
    """渲染模块客户端"""
    __mVersion__ = 7
    __identifier__ = ModuleEnum.identifier

    def __init__(self):
        super(RenderModuleClient, self).__init__()
        self.system.SetModConfigParser(RenderParser())

        self.load_data = False
        self.ui_finished_created = False
        self.render_player = set()
        # 检测过的实体
        self.check_engine_type = set()

    def ConfigEvent(self):
        super(RenderModuleClient, self).ConfigEvent()
        self.defaultEvent.update({
            ClientEvent.AddPlayerCreatedClientEvent: self.AddPlayerCreatedClientEvent,
            ClientEvent.AddEntityClientEvent: self.AddEntityClientEvent,
            ClientEvent.UiInitFinished: self.UiInitFinished,
        })
        self.serverEvent.update({
            ModuleEvent.ModuleRequestSynRenderDataEvent: self.ModuleRequestSynRenderDataEvent,
            ServerEvent.RequestRenderEntityEvent: self.RequestRenderEntityEvent
        })

        # -----------------------------------------------------------------------------------

    def BuildPlayerRenderData(self, player_id):
        # type: (str) -> None
        """构建玩家渲染"""
        # print "[info]", "building render: %s" % player_id
        config = ModuleRender.PlayerRenderData
        if not config:
            return
        render_comp = self.comp_factory.CreateActorRender(player_id)

        # 渲染资源动态导入
        for key, path in config["textures"].iteritems():
            render_comp.AddPlayerTexture(key, path)
        for key, path in config["geometries"].iteritems():
            render_comp.AddPlayerGeometry(key, path)
        for key, value in config["animations"].iteritems():
            render_comp.AddPlayerAnimation(key, value)
        for key, path in config["animation_controllers"].iteritems():
            render_comp.AddPlayerAnimationController(key, path)
        for key, condition in config["render_controllers"].iteritems():
            if not render_comp.AddPlayerRenderController(key, condition):
                render_comp.RemovePlayerRenderController(key)
                render_comp.AddPlayerRenderController(key, condition)
        for key, condition in config["scripts"].iteritems():
            if not render_comp.AddActorScriptAnimate(GameEntity.player, key, condition):
                render_comp.AddActorScriptAnimate(GameEntity.player, key, condition, True)
        for key, path in config["materials"].iteritems():
            render_comp.AddPlayerRenderMaterial(key, path)
        for key, path in config["particles"].iteritems():
            render_comp.AddPlayerParticleEffect(key, path)
        for key, path in config["sounds"].iteritems():
            render_comp.AddPlayerSoundEffect(key, path)

        render_comp.RebuildPlayerRender()

    def BuildEntityRenderData(self, entity_id, engine_type):
        # type: (str, str) -> None
        """构建生物渲染"""
        render_comp = self.comp_factory.CreateActorRender(entity_id)

        global_render = ModuleRender.GlobalRenderData
        mob_render = ModuleRender.MobRenderData[engine_type]  # type: dict

        # 渲染资源动态导入
        for key, path in mob_render["textures"].items() + global_render.get("textures", []):
            render_comp.AddActorTexture(engine_type, key, path)
        for key, path in mob_render["geometries"].items() + global_render.get("geometries", []):
            render_comp.AddActorGeometry(engine_type, key, path)
        for key, value in mob_render["animations"].items() + global_render.get("animations", []):
            render_comp.AddActorAnimation(engine_type, key, value)
        for key, path in mob_render["animation_controllers"].items() + global_render.get("animation_controllers", []):
            render_comp.AddActorAnimationController(engine_type, key, path)
        for key, condition in mob_render["render_controllers"].items() + global_render.get("render_controllers", []):
            if not render_comp.AddActorRenderController(engine_type, key, condition):
                render_comp.RemoveActorRenderController(engine_type, key)
                render_comp.AddActorRenderController(engine_type, key, condition)
        for key, condition in mob_render["scripts"].items() + global_render.get("scripts", []):
            if not render_comp.AddActorScriptAnimate(engine_type, key, condition):
                render_comp.AddActorScriptAnimate(engine_type, key, condition, True)
        for key, path in mob_render["materials"].items() + global_render.get("materials", []):
            render_comp.AddActorRenderMaterial(engine_type, key, path)
        for key, path in mob_render["particles"].items() + global_render.get("particles", []):
            render_comp.AddActorParticleEffect(engine_type, key, path)
        for key, path in mob_render["sounds"].items() + global_render.get("sounds", []):
            render_comp.AddActorSoundEffect(engine_type, key, path)

        render_comp.RebuildActorRender(engine_type)

    def RawBuildPlayerRender(self, player_id, config):
        # type: (str, dict) -> None
        """构建玩家渲染"""
        render_comp = self.comp_factory.CreateActorRender(player_id)

        # 渲染资源动态导入
        for key, path in config.get("textures", {}).iteritems():
            render_comp.AddPlayerTexture(key, path)
        for key, path in config.get("geometries", {}).iteritems():
            render_comp.AddPlayerGeometry(key, path)
        for key, value in config.get("animations", {}).iteritems():
            render_comp.AddPlayerAnimation(key, value)
        for key, path in config.get("animation_controllers", {}).iteritems():
            render_comp.AddPlayerAnimationController(key, path)
        for key, condition in config.get("render_controllers", {}).iteritems():
            if not render_comp.AddPlayerRenderController(key, condition):
                render_comp.RemovePlayerRenderController(key)
                render_comp.AddPlayerRenderController(key, condition)
        for key, condition in config.get("scripts", {}).iteritems():
            if not render_comp.AddActorScriptAnimate(GameEntity.player, key, condition):
                render_comp.AddActorScriptAnimate(GameEntity.player, key, condition, True)
        for key, path in config.get("materials", {}).iteritems():
            render_comp.AddPlayerRenderMaterial(key, path)
        for key, path in config.get("particles", {}).iteritems():
            render_comp.AddPlayerParticleEffect(key, path)
        for key, path in config.get("sounds", {}).iteritems():
            render_comp.AddPlayerSoundEffect(key, path)

        # render_comp.RebuildPlayerRender()

    def RawBuildEntityRender(self, entity_id, config):
        # type: (str, dict) -> None
        """构建生物渲染"""
        render_comp = self.comp_factory.CreateActorRender(entity_id)
        engine_type = RawEntity.GetTypeStr(entity_id)
        for key, path in config.get("textures", {}).items():
            render_comp.AddActorTexture(engine_type, key, path)
        for key, path in config.get("geometries", {}).items():
            render_comp.AddActorGeometry(engine_type, key, path)
        for key, value in config.get("animations", {}).items():
            render_comp.AddActorAnimation(engine_type, key, value)
        for key, path in config.get("animation_controllers", {}).items():
            render_comp.AddActorAnimationController(engine_type, key, path)
        for key, condition in config.get("render_controllers", {}).items():
            if not render_comp.AddActorRenderController(engine_type, key, condition):
                render_comp.RemoveActorRenderController(engine_type, key)
                render_comp.AddActorRenderController(engine_type, key, condition)
        for key, condition in config.get("scripts", {}).items():
            if not render_comp.AddActorScriptAnimate(engine_type, key, condition):
                render_comp.AddActorScriptAnimate(engine_type, key, condition, True)
        for key, path in config.get("materials", {}).items():
            render_comp.AddActorRenderMaterial(engine_type, key, path)
        for key, path in config.get("particles", {}).items():
            render_comp.AddActorParticleEffect(engine_type, key, path)
        for key, path in config.get("sounds", {}).items():
            render_comp.AddActorSoundEffect(engine_type, key, path)

        # render_comp.RebuildActorRender(engine_type)

    # -----------------------------------------------------------------------------------

    def ModuleRequestSynRenderDataEvent(self, args):
        ModuleRender.GlobalRenderData = args["global"]
        ModuleRender.PlayerRenderData = args["player"]
        ModuleRender.MobRenderData = args["mob"]
        self.load_data = True
        if self.ui_finished_created:
            for player_id in self.render_player:
                self.BuildPlayerRenderData(player_id)
            self.render_player.clear()

    def AddPlayerCreatedClientEvent(self, args):
        player_id = args["playerId"]
        if not self.load_data or not self.ui_finished_created:
            self.render_player.add(player_id)
            return
        self.BuildPlayerRenderData(player_id)

    def UiInitFinished(self, args):
        self.ui_finished_created = True
        if self.load_data:
            for player_id in self.render_player:
                self.BuildPlayerRenderData(player_id)
            self.render_player.clear()

    def AddEntityClientEvent(self, args):
        entity_id = args["id"]
        engine_type = args["engineTypeStr"]
        if engine_type in self.check_engine_type:
            return
        self.check_engine_type.add(engine_type)
        if ModuleRender.GlobalRenderData or engine_type in ModuleRender.MobRenderData.keys():
            self.BuildEntityRenderData(entity_id, engine_type)

    # 请求动态渲染生物事件
    def RequestRenderEntityEvent(self, args):
        """请求动态渲染生物事件"""
        entity_id = args["entityId"]
        config = args["config"]
        if RawEntity.IsPlayer(entity_id):
            self.RawBuildPlayerRender(entity_id, config)
        else:
            self.RawBuildEntityRender(entity_id, config)
