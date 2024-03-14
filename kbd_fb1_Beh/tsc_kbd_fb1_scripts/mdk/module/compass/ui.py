# -*- coding:utf-8 -*-


import mod.client.extraClientApi as clientApi

from ...client.entity import RawEntity
from ...common.system.base import ClientEvent
from ...common.utils.space import *
from ...ui.module.base import UIPreset

view_binder = clientApi.GetViewBinderCls()


class CompassScreen(UIPreset):
    """指南针界面"""
    __mVersion__ = 5

    def __init__(self, namespace, name, param):
        super(CompassScreen, self).__init__(namespace, name, param)
        self.direction_map = {
            "north": ("N", 0.0),
            "east": ("E", 90.0),
            "south": ("S", 180.0),
            "west": ("W", 270.0),
        }
        self.mark_pos = {}  # path: pos
        self.dir_label = None

        self.pre_yaw = 0

        self.active = False
        self.screen_mark = None
        self.tip_screen = None

    def ConfigEvent(self):
        super(CompassScreen, self).ConfigEvent()
        self.defaultEvent.update({
            ClientEvent.OnKeyPressInGame: self.OnKeyPressInGame
        })

    def Create(self):
        super(CompassScreen, self).Create()
        self.SetVisible("/panel_compass/image/panel/mark", False)
        self.dir_label = self.GetLabelUIControl("/panel_compass/image/panel/label")

    @view_binder.binding(view_binder.BF_BindString, "#compass_screen.game_tick")
    def GameTick(self):
        self.UpdateDirectionMark()
        self.UpdateLocationMark()
        if self.active:
            self.UpdateScreenMark()

    # -----------------------------------------------------------------------------------

    """方向导航相关"""

    def UpdateDirectionMark(self):
        direction = "west"
        pitch, self.pre_yaw = self.local_player.GetRot()
        self.pre_yaw += 225
        if self.pre_yaw // 360:
            self.pre_yaw -= 360
        if self.pre_yaw < 90:
            direction = "north"
        elif self.pre_yaw < 180:
            direction = "east"
        elif self.pre_yaw < 270:
            direction = "south"
        mark, Dm = self.direction_map[direction]
        rate = (Dm + 90 - self.pre_yaw) / 90
        sizeX, _ = self.GetCompSize("/panel_compass/image/panel")
        labelSizeX, _ = self.dir_label.GetSize()
        self.dir_label.SetPosition((rate * (sizeX - labelSizeX), 0))
        self.dir_label.SetText(mark)

    # -----------------------------------------------------------------------------------

    """目标点相关"""

    def CreateLocationMark(self, mark, pos, texture):
        parent = "/panel_compass/image/panel"
        path = self.CloneComp(parent + "/mark", parent, mark)
        # 缓存目标点数据
        self.mark_pos[mark] = (path, pos, texture)
        image = self.GetImageUIControl(path)
        image.SetVisible(True)
        # image.SetSprite(texture)

    def UpdateLocationMark(self):
        """更新位置标记"""
        if not self.mark_pos:
            return
        foot_pos = self.local_player.GetPos()
        sizeX, sizeY = self.GetCompSize("/panel_compass/image/panel")
        playerRot = self.local_player.GetRot()
        for config in self.mark_pos.values():
            path, pos, texture = config
            comp = self.GetBaseUIControl(path)
            compSizeX, compSizeY = comp.GetSize()

            angle = math.atan2(pos[2] - foot_pos[2], pos[0] - foot_pos[0]) * 180 / math.pi
            angle = (angle - playerRot[1]) % 360
            percent = angle / 180.0
            if percent >= 1.5:
                percent = 0
            elif percent > 1.0:
                percent = 1
            scale = Misc.GetDistBetween(pos, foot_pos)
            scale = (25.0 - scale) / 25
            if scale < 0:
                scale = 1
            else:
                scale = 1 + scale / 2.5
            size = sizeY * scale
            comp.SetSize((size,) * 2)
            comp.SetPosition((percent * (sizeX - compSizeX), -(size - sizeY) / 2.0))

    # -----------------------------------------------------------------------------------

    """屏幕标记相关"""

    def UpdateScreenMark(self):
        if isinstance(self.screen_mark, str):
            if not self.game_comp.IsEntityAlive(self.screen_mark):
                self.active = False
                self.screen_mark = None
                return
            target_pos = Misc.GetPosModify(RawEntity.GetPos(self.screen_mark), (0, 1.5, 0))
        else:
            target_pos = self.screen_mark

        width, height = self.game_comp.GetScreenSize()
        camera_pos = self.camera_comp.GetPosition()
        fov = self.camera_comp.GetFov()
        fov = fov / 180.0 * math.pi * 1.1
        ratio = width / height
        view_matrix = SpaceMatrix.GetViewMatrix(camera_pos, Misc.GetPosModify(camera_pos, self.camera_comp.GetForward()))
        projection_matrix = SpaceMatrix.GetProjectionMatrix(fov, ratio, 0.1, 100)
        matrix = projection_matrix.Cross(view_matrix)
        matrix = matrix.Cross(Matrix(
            (target_pos[0],),
            (target_pos[1],),
            (target_pos[2],),
            (1.0,),
        ))
        matrix_vec = Vector(*matrix.transposition.mat[0])
        matrix_vec /= matrix_vec[3]
        vec_x, vec_y, z_view = matrix_vec[0], matrix_vec[1], matrix_vec[3]
        check_dir = matrix_vec[2]
        render = True
        if check_dir < 1.002:
            render = False
        # 视口变化
        pos_x = (vec_x / 2.0 + 0.5) * width
        pos_y = (vec_y / 2.0 + 0.5) * height
        # self.tip_screen.SetUITips("\n".join([
        #     "矩阵转换：<%s %s> <%s>" % (round(vec_x, 2), round(vec_y, 2), round(check_dir, 5)),
        #     "屏幕位置：<%s %s> <%s>" % (round(pos_x, 1), round(pos_y, 1), round(z_view, 1)),
        #     "屏幕信息：<%s %s> ratio: %s fov: %s" % (width, height, ratio, fov),
        # ]))
        if render:
            image = self.GetImageUIControl("/panel_mark/marker")
            center = self.GetCompCenterPos("/panel_mark/marker")
            screen_pos = Misc.GetPosModify((pos_x, pos_y), center, method="sub")
            image.SetPosition(screen_pos)
            distance = self.GetDistanceBetweenPos(target_pos)
            self.SetLabelText("/panel_mark/marker/label", "%sm" % round(distance, 1))

    # -----------------------------------------------------------------------------------

    def OnKeyPressInGame(self, args):
        screen, is_down, key = super(CompassScreen, self).OnKeyPressInGame(args)
        if not is_down:
            return
        # elif key == KeyBoardType.KEY_H:
        #     self.tip_screen = None
        #     if not self.tip_screen:
        #         self.tip_screen = self.GetUINode("")
        #     self.active = not self.active
        # elif key == KeyBoardType.KEY_K:
        #     entity_id = self.GetAimEntity()
        #     if entity_id:
        #         self.screen_mark = entity_id
        #     else:
        #         self.screen_mark = Misc.GetPosModify(self.GetAimBlock()["pos"], (0.5, 0.5, 0.5))
