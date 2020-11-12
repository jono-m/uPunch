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
        r.setSize(QSizeF(self.radius * 2, self.radius * 2))
        r.moveCenter(self.center)
        return r

    def GetTransformed(self, scale=1, rotation=0, offset=QPointF(), flipY=False):
        newCircle = Circle(self.center, self.radius, self.layer, self.specificallyIgnored)
        if flipY:
            newCircle.center.setY(-newCircle.center.y())
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
        self._circles: typing.List[Circle] = []
        self._layers: typing.Dict[str, bool] = {}

        self.rect = QRectF()

        self.circleA: typing.Optional[Circle] = None
        self.circleB: typing.Optional[Circle] = None

        self._scale = 0
        self._rotation = 0
        self._offset = QPointF()
        self._flipY = False

        self.filename = ""

        self.LoadFromDXFFile("500kCartridge.dxf")

    def GetLayers(self):
        return self._layers.copy()

    def SetLayerEnabled(self, layerName: str, enabled: bool):
        self._layers[layerName] = enabled

        if not enabled:
            if self.circleA is not None and self.circleA.layer == layerName:
                self.circleA = None
            if self.circleB is not None and self.circleB.layer == layerName:
                self.circleB = None

    def LoadFromDXFFile(self, filename) -> typing.Optional[str]:
        self.filename = filename

        modelSpace = ezdxf.readfile(filename).modelspace()

        self._circles = self.ExtractCircles(modelSpace)

        self._layers = {}
        self.rect = None
        for circle in self._circles:
            if self.rect is None:
                self.rect = circle.GetRect()
            else:
                self.rect = self.rect.united(circle.GetRect())
            if circle.layer not in self._layers:
                self._layers[circle.layer] = True

        return None

    def ExtractCircles(self, space: ezdxf.layouts.BaseLayout) -> typing.List[Circle]:
        circleResults = space.query('CIRCLE')
        circles = [Circle(QPointF(entity.dxf.center.x, entity.dxf.center.y) / 1000,
                          entity.dxf.radius / 1000,
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
                                                                 insertResult.dxf.insert.y) / 1000)
                transformed.layer = insertResult.dxf.layer
                circles.append(transformed)
        return circles

    def GetLocalCircles(self):
        return [c for c in self._circles if self._layers[c.layer]]

    def GetTransformedCircles(self):
        return [circle.GetTransformed(self._scale, self._rotation, self._offset, self._flipY) for circle in
                self._circles]
