import typing
import math
from PySide2.QtCore import *
import ezdxf
import ezdxf.layouts
from ezdxf.entities.insert import Insert


class Circle:
    def __init__(self, center: QPointF, layers: typing.List[str], specificallyIgnored: bool, blocks: typing.List[str]):
        self.center = center
        self.layers = layers
        self.blocks = blocks
        self.specificallyIgnored = specificallyIgnored

    def Copy(self):
        return Circle(self.center, self.layers, self.specificallyIgnored, self.blocks)

    def GetTransformed(self, scale=1, rotation=0, offset=QPointF()):
        newCircle = self.Copy()

        newCircle.center = newCircle.center * scale
        newCircle.center = rotate(newCircle.center, rotation) + offset
        return newCircle

    def GetRect(self):
        r = QRectF()
        r.moveCenter(self.center)
        r.setSize(QSizeF(1, 1))
        return r


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

        self.ignoreRotation = False
        self.ignoreScale = False

        self.filename = ""

    def GetLayers(self):
        return self._layers.copy()

    def GetBlocks(self):
        return self._blocks.copy()

    def SetLayerEnabled(self, layerName: str, enabled: bool):
        self._layers[layerName] = enabled
        if not enabled:
            if not self.IsCircleOn(self.circleA):
                self.circleA = None
            if not self.IsCircleOn(self.circleB):
                self.circleB = None

    def IsCircleOn(self, circle: typing.Optional[Circle]):
        if circle is None:
            return False

        aLayerOn = False
        aBlockOn = False
        for layer in circle.layers:
            if self._layers[layer]:
                aLayerOn = True
                break
        for block in circle.blocks:
            if block is None or self._blocks[block]:
                aBlockOn = True
                break
        return aLayerOn and aBlockOn

    def SetBlockEnabled(self, blockName: str, enabled: bool):
        self._blocks[blockName] = enabled

        if not enabled:
            if not self.IsCircleOn(self.circleA):
                self.circleA = None
            if not self.IsCircleOn(self.circleB):
                self.circleB = None

    def LoadFromDXFFile(self, filename) -> typing.Optional[str]:
        self.filename = filename

        modelSpace = ezdxf.readfile(filename).modelspace()

        circles = self.ExtractCircles(modelSpace)
        centerCircleDict: typing.Dict[typing.Tuple[float, float], Circle] = {}
        print("Done")
        for c in circles:
            center = (c.center.x(), c.center.y())
            if center in centerCircleDict:
                centerCircleDict[center].layers.append(c.layers[0])
                centerCircleDict[center].blocks.append(c.blocks[0])
            else:
                centerCircleDict[center] = c

        self._circles = list(centerCircleDict.values())

        self._layers = {}
        self._blocks = {}
        for circle in self._circles:
            for layer in circle.layers:
                if layer not in self._layers:
                    self._layers[layer] = True
            for block in circle.blocks:
                if block is not None and block not in self._blocks:
                    self._blocks[block] = True

        return None

    def ExtractCircles(self, space: ezdxf.layouts.BaseLayout) -> typing.List[Circle]:
        circleResults = space.query('CIRCLE')
        circles = [Circle(QPointF(entity.dxf.center.x, entity.dxf.center.y) / 1000,
                          [entity.dxf.layer],
                          False,
                          [None])
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
                circles.append(Circle(QPointF(insertResult.dxf.insert.x, insertResult.dxf.insert.y) / 1000,
                                      [insertResult.dxf.layer],
                                      False,
                                      [insertResult.dxf.name]))
        return circles

    def GetLocalCircles(self):
        return [c for c in self._circles if self.IsCircleOn(c)]

    def CalculateScale(self):
        if self.circleA is None or self.circleB is None or self.ignoreScale:
            return 1
        localA = self.circleA.center
        localB = self.circleB.center
        if not self.flipY:
            localA = QPointF(localA.x(), -localA.y())
            localB = QPointF(localB.x(), -localB.y())

        localDist = distance(localA, localB)
        globalDist = distance(self.globalA, self.globalB)
        if localDist == 0:
            return 0
        else:
            return globalDist / localDist

    def CalculateRotation(self):
        if self.circleA is None or self.circleB is None or self.ignoreRotation:
            return 0
        localA = self.circleA.center
        localB = self.circleB.center
        if not self.flipY:
            localA = QPointF(localA.x(), -localA.y())
            localB = QPointF(localB.x(), -localB.y())

        return signedAngle(localB - localA, self.globalB - self.globalA)

    def GetAlignedCircles(self):
        localCircles = [c.Copy() for c in self.GetLocalCircles()]
        if self.circleA is None or self.circleB is None:
            return localCircles

        localA = self.circleA.center
        localB = self.circleB.center
        if not self.flipY:
            for c in localCircles:
                c.center = QPointF(c.center.x(), -c.center.y())
            localA = QPointF(localA.x(), -localA.y())
            localB = QPointF(localB.x(), -localB.y())

        theta = self.CalculateRotation()
        scale = self.CalculateScale()

        globalCircles = []
        for c in localCircles:
            transformedCircle = c.Copy()
            transformedCircle.center = transformedCircle.center - localA  # Relative to A
            transformedCircle.center = transformedCircle.center * scale  # scaled
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
