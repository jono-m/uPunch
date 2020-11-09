from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtCore import *
import typing


class StageRectGraphicsItem(QGraphicsRectItem):
    def __init__(self):
        super().__init__()

        self.lineThickness = 1
        self.lineSpacing = 10
        self.lineColor = QColor(70, 70, 70)

        self.scale = 1

        self.showX = True
        self.showY = True

        self.setBrush(QBrush(QColor(50, 50, 50)))
        self.setPen(Qt.NoPen)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: typing.Optional[QWidget] = ...):
        super().paint(painter, option, widget)

        pen = QPen(self.lineColor)
        pen.setWidthF(self.lineThickness/self.scale)
        painter.setPen(pen)

        if self.showX:
            nX = int(self.rect().width() / self.lineSpacing)
            for iX in range(nX):
                x = iX * self.lineSpacing + self.rect().left()
                yMin = self.rect().top()
                yMax = self.rect().bottom()
                painter.drawLine(QLineF(QPointF(x, yMin), QPointF(x, yMax)))

        if self.showY:
            nY = int(self.rect().height() / self.lineSpacing)
            for iY in range(nY):
                y = iY * self.lineSpacing + self.rect().top()
                xMin = self.rect().left()
                xMax = self.rect().right()
                painter.drawLine(QLineF(QPointF(xMin, y), QPointF(xMax, y)))
