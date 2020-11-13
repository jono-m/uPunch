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

    def Copy(self):
        return Circle(self.center, self.radius, self.layer, self.specificallyIgnored)

    def GetRect(self):
        r = QRectF()
        r.setSize(QSizeF(self.radius * 2, self.radius * 2))
        r.moveCenter(self.center)
        return r

    def GetTransformed(self, scale=1, rotation=0, offset=QPointF()):
        newCircle = self.Copy()

        newCircle.radius = newCircle.radius * scale
        newCircle.center = newCircle.center * scale
        newCircle.center = rotate(newCircle.center, rotation) + offset
        return newCircle


class Design:
    def __init__(self):
        self._circles: typing.List[Circle] = []
        self._layers: typing.Dict[str, bool] = {}

        self.rect = QRectF()

        self.circleA: typing.Optional[Circle] = None
        self.circleB: typing.Optional[Circle] = None

        self.globalA = QPointF()
        self.globalB = QPointF()
        self.flipY = False

        self.filename = ""

        self.LoadFromDXFFile("test.dxf")

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

        if len(self._circles) >= 2:
            self.circleA = self._circles[0]
            self.circleB = self._circles[1]

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
                                                         QPointF(insertResult.dxf.insert.x / 1000,
                                                                 insertResult.dxf.insert.y / 1000))
                transformed.layer = insertResult.dxf.layer
                circles.append(transformed)
        return circles

    def GetLocalCircles(self):
        return [c for c in self._circles if self._layers[c.layer]]

    def GetAlignedCircles(self):
        localCircles = [c.Copy() for c in self.GetLocalCircles()]
        localA = self.circleA.center
        localB = self.circleB.center
        if self.flipY:
            for c in localCircles:
                c.center = QPointF(c.center.x(), -c.center.y())
            localA = QPointF(localA.x(), -localA.y())
            localB = QPointF(localB.x(), -localB.y())

        localDist = distance(localA, localB)
        globalDist = distance(self.globalA, self.globalB)
        if localDist == 0:
            s = 0
        else:
            s = globalDist / localDist

        theta = signedAngle(localB-localA, self.globalB - self.globalA)
        globalCircles = []
        for c in localCircles:
            transformedCircle = c.Copy()
            transformedCircle.center = transformedCircle.center - localA  # Relative to A
            transformedCircle.center = transformedCircle.center * s  # scaled
            transformedCircle.center = rotate(transformedCircle.center, theta)  # rotated
            transformedCircle.center = transformedCircle.center + self.globalA  # Relative to global A
            globalCircles.append(transformedCircle)

        return globalCircles


def rotate(a: QPointF, theta):
    x = math.cos(theta) * a.x() - math.sin(theta) * a.y()
    y = math.sin(theta) * a.x() + math.cos(theta) * a.y()
    return QPointF(x, y)


def signedAngle(a: QPointF, b: QPointF):
    if a == QPointF() or b == QPointF():
        return 0
    dot = a.x() * b.x() + a.y() * b.y()  # dot product
    det = a.x() * b.y() - a.y() * b.x()  # determinant
    angle = math.atan2(det, dot)  # atan2(y, x) or atan2(sin, cos)
    return angle


def distance(a: QPointF, b: QPointF):
    return math.sqrt((a.x() - b.x()) ** 2 + (a.y() - b.y()) ** 2)
