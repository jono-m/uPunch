import typing
import math
from PySide2.QtCore import *
import ezdxf


class Circle:
    def __init__(self, center: QPointF, radius: float, layer: str, specificallyIgnored: bool):
        self.center = center
        self.radius = radius
        self.layer = layer
        self.specificallyIgnored = specificallyIgnored

    def GetTransformed(self, scale=1, rotation=0, offset=QPointF()):
        newCircle = Circle(self.center, self.radius, self.layer, self.specificallyIgnored)
        c = math.cos(rotation)
        s = math.sin(rotation)
        newCircle.radius = newCircle.radius * scale
        newCircle.center = newCircle.center * scale
        x0 = newCircle.center[0]
        y0 = newCircle.center[1]
        x1 = x0 * c - y0 * s
        y1 = x0 * s + y0 * c
        newCircle.center = QPointF(x1, y1) + offset
        return newCircle


class Design:
    def __init__(self, circles: typing.List[Circle]):
        self._circles = circles

    @staticmethod
    def GetFromDXFFile(filename) -> 'Design':
        modelSpace = ezdxf.readfile(filename).modelspace()

        results = modelSpace.query('CIRCLE')
        circles = [Circle(QPointF(entity.dxf.center.x, entity.dxf.center.y),
                          entity.dxf.center.radius,
                          entity.dxf.layer,
                          False)
                   for entity in results]

        return Design(circles)

    def GetLocalCircles(self):
        return self._circles

    def GetTransformed(self, scale=1, rotation=0, offset=QPointF()):
        return [circle.GetTransformed(scale, rotation, offset) for circle in self._circles]
