from PySide2.QtWidgets import *
from PySide2.QtGui import *
from Data.Design import *
from Util import *


class CADGraphicsItem(QGraphicsItem):
    def __init__(self, design: Design):
        super().__init__()

        self.design = design

        self.mainBrush = QBrush(QColor(100, 255, 100, 255))
        self.aBrush = QBrush(QColor(150, 150, 255, 255))
        self.bBrush = QBrush(QColor(150, 255, 255, 255))

        self.bR = QRectF()

        self.circles: typing.List[Circle] = []

        self.CacheCircles()

    def CacheCircles(self):
        self.prepareGeometryChange()
        self.circles = [c for c in self.design.GetAlignedCircles() if not c.specificallyIgnored]
        self.bR = None
        for c in self.circles:
            rect = c.GetRect()
            if self.bR is None:
                self.bR = rect
            else:
                self.bR = self.bR.united(rect)
        self.update()

    def boundingRect(self):
        if self.bR is None:
            return QRectF()
        else:
            return self.bR

    def paint(self, painter: QPainter, option, widget, PySide2_QtWidgets_QWidget=None, NoneType=None, *args, **kwargs):
        painter.setPen(Qt.NoPen)
        for c in self.circles:
            if c == self.design.circleA:
                painter.setBrush(self.aBrush)
            elif c == self.design.circleB:
                painter.setBrush(self.bBrush)
            else:
                painter.setBrush(self.mainBrush)

            painter.drawEllipse(c.GetRect())
