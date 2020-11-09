from PySide2.QtCore import *
from PySide2.QtGui import *


def ClampFloat(value: float, minVal: float, maxVal: float):
    return min(maxVal, max(value, minVal))


class Bounds3D:
    def __init__(self, pMin: QVector3D, pMax: QVector3D):
        self.pMin = pMin
        self.pMax = pMax

    def InsideBounds(self, point: QVector3D):
        return QVector3D(ClampFloat(point.x(), self.pMin.x(), self.pMax.x()),
                         ClampFloat(point.y(), self.pMin.y(), self.pMax.y()),
                         ClampFloat(point.z(), self.pMin.z(), self.pMax.z()))
