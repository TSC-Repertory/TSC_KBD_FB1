# -*- coding:utf-8 -*-


from misc import *


class Matrix(object):
    """矩阵"""

    def __init__(self, *data):
        self.mat = data
        self._mat_row = len(self.mat)
        self._mat_col = len(self.mat[0])

    def __str__(self):
        texts = ["Matrix[", ]
        for row in xrange(self._mat_row):
            text = []
            for col in xrange(self._mat_col):
                text.append(str(self.mat[row][col]))
            texts.append("[%s]" % ", ".join(text))
        texts.append("]")
        return "\n".join(texts)

    def __getitem__(self, index):
        """获得向量索引值"""
        if index > self._mat_row:
            return None
        return self.mat[index]

    # -----------------------------------------------------------------------------------

    @property
    def row(self):
        # type: () -> int
        """矩阵的行"""
        return self._mat_row

    @property
    def column(self):
        # type: () -> int
        """矩阵的列"""
        return self._mat_col

    @property
    def transposition(self):
        # type: () -> Matrix
        """获得转置矩阵"""
        res = []
        for col in xrange(self._mat_col):
            unit = []
            for row in xrange(self._mat_row):
                unit.append(self.mat[row][col])
            res.append(tuple(unit))
        return Matrix(*res)

    def inverse(self):
        # type: () -> Matrix
        """矩阵的逆"""

    def Dot(self, matrix):
        """
        矩阵点乘\n
        - 矩阵各对应元素相乘
        - 需要矩阵行数相同
        - 需要左矩阵列数为1或等于右矩阵列数
        """
        assert isinstance(matrix, Matrix)
        res = []
        if self._mat_row != matrix.row:
            print "[warn]", "行数不相等"
            return
        if self._mat_col != matrix.column and self._mat_col > 1:
            print "[warn]", "列数不相等"
            return
        for row in xrange(self._mat_row):
            if self._mat_col == 1:
                res.append((Vector(*matrix.mat[row]) * self.mat[row][0]).ToList())
                continue
            row_data = []
            for col in xrange(matrix.column):
                row_data.append(self.mat[row][col] * matrix.mat[row][col])
            res.append(row_data)

        return Matrix(*res)

    def Cross(self, matrix):
        """
        矩阵叉乘\n
        - 需要左矩阵列等于右矩阵行
        """
        assert isinstance(matrix, Matrix)
        if self._mat_col != matrix.row:
            print "[warn]", "列行不相等: %s|%s" % (self._mat_col, matrix.row)
            return None
        res = [[0 for _ in xrange(matrix.column)] for _ in xrange(self._mat_row)]
        for row in xrange(self._mat_row):
            for col in xrange(matrix.column):
                for index in xrange(self._mat_col):
                    res[row][col] += self.mat[row][index] * matrix.mat[index][col]
        return Matrix(*res)


class SpaceMatrix(object):
    """空间矩阵"""

    @classmethod
    def GetViewMatrix(cls, camera, target):
        """
        获得观察矩阵\n
        url: https://zhuanlan.zhihu.com/p/552252893\n
        - camera: tuple 相机位置
        - target: tuple 目标位置
        """
        camera = MVector3(*camera)
        forward = (camera - MVector3(*target)).Normalize()
        right = MVector3(*forward.Cross((0, 1, 0))).Normalize()
        up = MVector3(*right.Cross(forward)).Normalize()
        return Matrix(
            (right[0], right[1], right[2], -right.Dot(camera)),
            (up[0], up[1], up[2], -up.Dot(camera)),
            (-forward[0], -forward[1], -forward[2], forward.Dot(camera)),
            (0, 0, 0, 1.0),
        )

    @classmethod
    def GetProjectionMatrix(cls, fov, aspect, near, far):
        """
        获得透视投影矩阵\n
        - fov: float 视野
        - aspect: float 屏幕宽高比
        - near: float 裁剪面近面距离
        - far: float 裁剪面远面距离
        """
        data = 1 / (math.tan(fov / 2.0))
        return Matrix(
            (data / aspect, 0, 0, 0),
            (0, data, 0, 0),
            (0, 0, 1.0 * (near + far) / (near - far), 2.0 * near * far / (near - far)),
            (0, 0, -1.0, 0)
        )


if __name__ == '__main__':
    pass
    # mat1 = Matrix((1, 2, 3, 4), (4, 5, 6, 7), (3, 4, 5, 6), (5, 6, 7, 8))
    # print mat1
    # mat2 = Matrix((1, ), (3, ), (5, ), (7, ))
    # print mat2
    # mat3 = Matrix((2, 4, 5), (4, 6, 7))
    # print mat3
    # print mat1.Dot(mat3)
    # print mat1.Cross(mat2)
    # print SpaceMatrix.GetViewMatrix((0, 100, 0), (50, 105, 50))
    # print SpaceMatrix.GetProjectionMatrix(45.0, 0.8, 10, 100)
