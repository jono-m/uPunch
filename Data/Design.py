import typing
import math
from PySide2.QtCore import *
import ezdxf
import ezdxf.layouts
from ezdxf.entities.insert import Insert


class Circle:
    def __init__(self, center: QPointF, radius: float, layer: str, specificallyIgnored: bool):
        self.center = center
        self.radius = radius
        self.layer = layer
        self.specificallyIgnored = specificallyIgnored

    def GetRect(self):
        r = QRectF()
        r.setSize(QSizeF(self.radius*2, self.radius*2))
        r.moveCenter(self.center)
        return r

    def GetTransformed(self, scale=1, rotation=0, offset=QPointF()):
        newCircle = Circle(self.center, self.radius, self.layer, self.specificallyIgnored)
        c = math.cos(rotation)
        s = math.sin(rotation)
        newCircle.radius = newCircle.radius * scale
        newCircle.center = newCircle.center * scale
        x0 = newCircle.center.x()
        y0 = newCircle.center.y()
        x1 = x0 * c - y0 * s
        y1 = x0 * s + y0 * c
        newCircle.center = QPointF(x1, y1) + offset
        return newCircle


class Design:
    def __init__(self):
        self.circles: typing.List[Circle] = []
        self.layers: typing.Dict[str, bool] = {}

        self.rect = QRectF()

    def LoadFromDXFFile(self, filename) -> 'Design':
        modelSpace = ezdxf.readfile(filename).modelspace()

        self.circles = self.ExtractCircles(modelSpace)

        self.layers = {}
        self.rect = None
        for circle in self.circles:
            if self.rect is None:
                self.rect = circle.GetRect()
            else:
                self.rect = self.rect.united(circle.GetRect())
            if circle.layer not in self.layers:
                self.layers[circle.layer] = True

    def ExtractCircles(self, space: ezdxf.layouts.BaseLayout) -> typing.List[Circle]:
        circleResults = space.query('CIRCLE')
        circles = [Circle(QPointF(entity.dxf.center.x, entity.dxf.center.y),
                          entity.dxf.radius,
                          entity.dxf.layer,
                          False)
                   for entity in circleResults]
        insertResults = space.query('INSERT')
        for insertResult in insertResults:
            insertResult: Insert = insertResult
            space = insertResult.block()
            spaceCircles = self.ExtractCircles(space)
            for spaceCircle in spaceCircles:
                transformed = spaceCircle.GetTransformed(insertResult.dxf.xscale, insertResult.dxf.rotation,
                                                          QPointF(insertResult.dxf.insert.x,
                                                                  insertResult.dxf.insert.y))
                transformed.layer = insertResult.dxf.layer
                circles.append(transformed)
        return circles

    def GetLocalCircles(self):
        return [c for c in self.circles if self.layers[c.layer]]

    def GetTransformedCircles(self, scale=1, rotation=0, offset=QPointF()):
        return [circle.GetTransformed(scale, rotation, offset) for circle in self.circles]
