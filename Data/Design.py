import typing
import math
from PySide2.QtCore import *
import ezdxf
import ezdxf.layouts
from ezdxf.entities.insert import Insert


class Circle:
    def __init__(self, center: QPointF, layer: str, specificallyIgnored: bool, block: typing.Optional[str]):
        self.center = center
        self.layer = layer
        self.block = block
        self.specificallyIgnored = specificallyIgnored

    def Copy(self):
        return Circle(self.center, self.layer, self.specificallyIgnored, self.block)

    def GetTransformed(self, scale=1, rotation=0, offset=QPointF()):
        newCircle = self.Copy()

        newCircle.center = newCircle.center * scale
        newCircle.center = rotate(newCircle.center, rotation) + offset
        return newCircle


class Design:
    def __init__(self):
        self._circles: typing.List[Circle] = []
        self._layers: typing.Dict[str, bool] = {}
        self._blocks: typing.Dict[str, bool] = {}

        self.circleA: typing.Optional[Circle] = None
        self.circleB: typing.Optional[Circle] = None

        self.globalA = QPointF()
        self.globalB = QPointF()
        self.flipY = False

        self.filename = ""

    def GetLayers(self):
        return self._layers.copy()

    def GetBlocks(self):
        return self._blocks.copy()

    def SetLayerEnabled(self, layerName: str, enabled: bool):
        self._layers[layerName] = enabled

        if not enabled:
            if self.circleA is not None and self.circleA.layer == layerName:
                self.circleA = None
            if self.circleB is not None and self.circleB.layer == layerName:
                self.circleB = None

    def SetBlockEnabled(self, blockName: str, enabled: bool):
        self._blocks[blockName] = enabled

        if not enabled:
            if self.circleA is not None and self.circleA.block == blockName:
                self.circleA = None
            if self.circleB is not None and self.circleB.block == blockName:
                self.circleB = None

    def LoadFromDXFFile(self, filename) -> typing.Optional[str]:
        self.filename = filename

        modelSpace = ezdxf.readfile(filename).modelspace()

        circles = self.ExtractCircles(modelSpace)
        points = []
        self._circles = []
        for c in circles:
            if c.center not in points:
                self._circles.append(c)
                points.append(c.center)

        if len(self._circles) >= 2:
            self.circleA = self._circles[0]
            self.circleB = self._circles[1]

        self._layers = {}
        self._blocks = {}
        for circle in self._circles:
            if circle.layer not in self._layers:
                self._layers[circle.layer] = True
            if circle.block is not None and circle.block not in self._blocks:
                self._blocks[circle.block] = True

        return None

    def ExtractCircles(self, space: ezdxf.layouts.BaseLayout) -> typing.List[Circle]:
        circleResults = space.query('CIRCLE')
        circles = [Circle(QPointF(entity.dxf.center.x, entity.dxf.center.y) / 1000,
                          entity.dxf.layer,
                          False,
                          None)
                   for entity in circleResults]
        insertResults = space.query('INSERT')
        for insertResult in insertResults:
            insertResult: Insert = insertResult
            name = insertResult.dxf.name
            if name[0] == "*":
                space = insertResult.block()
                spaceCircles = self.ExtractCircles(space)
                for spaceCircle in spaceCircles:
                    transformed = spaceCircle.GetTransformed(insertResult.dxf.xscale, insertResult.dxf.rotation,
                                                             QPointF(insertResult.dxf.insert.x / 1000,
                                                                     insertResult.dxf.insert.y / 1000))
                    transformed.layer = insertResult.dxf.layer
                    circles.append(transformed)
            else:
                circles.append(Circle(QPointF(insertResult.dxf.insert.x, insertResult.dxf.insert.y)/1000,
                                      insertResult.dxf.layer,
                                      False,
                                      insertResult.dxf.name))
        return circles

    def GetLocalCircles(self):
        return [c for c in self._circles if self._layers[c.layer] and (c.block is None or self._blocks[c.block])]

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

        return [c for c in globalCircles if not c.specificallyIgnored]


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
