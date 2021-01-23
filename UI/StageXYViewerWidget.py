from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
from Data.StageSystem import *
from UI.StageRectGraphicsItem import *

import time


class StageXYViewerWidget(QGraphicsView):
    def __init__(self, stageSystem: StageSystem, control=True):
        super().__init__()

        self.stageSystem = stageSystem

        self.OnClicked = Event()

        self.setBackgroundBrush(QBrush(QColor(100, 100, 100)))

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setScene(QGraphicsScene())

        self.stageRect = StageRectGraphicsItem()
        self.scene().addItem(self.stageRect)

        self.indicator = self.scene().addEllipse(QRect(), Qt.NoPen, QBrush(QColor(255, 0, 0)))
        self.indicatorCoordinateDisplay = self.scene().addSimpleText("")
        self.indicatorHorLine = self.scene().addLine(QLineF())
        self.indicatorVertLine = self.scene().addLine(QLineF())

        self.coordinateDisplay = self.scene().addSimpleText("")
        self.coordinateDisplay.setBrush(QBrush(Qt.white))
        self.horLine = self.scene().addLine(QLineF())
        self.vertLine = self.scene().addLine(QLineF())

        self.setMinimumSize(500, 500)

        self.timer = QTimer()
        self.timer.timeout.connect(self.UpdateItems)
        self.timer.start(30)

        self.setMouseTracking(True)

        self.UpdateItems(True)

    def enterEvent(self, event: QEvent):
        if self.isEnabled():
            self.coordinateDisplay.setVisible(True)
            self.horLine.setVisible(True)
            self.vertLine.setVisible(True)

    def leaveEvent(self, event: QEvent):
        self.coordinateDisplay.setVisible(False)
        self.horLine.setVisible(False)
        self.vertLine.setVisible(False)

    def mousePressEvent(self, event: QMouseEvent):
        if self.isEnabled():
            pos = self.stageSystem.ClampPoint(self.mapToScene(event.localPos().toPoint()))
            self.OnClicked.Invoke(pos)
            self.setCursor(Qt.ArrowCursor)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.isEnabled() and not self.stageSystem.IsMoving():
            self.setCursor(Qt.PointingHandCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

        pos = self.stageSystem.ClampPoint(self.mapToScene(event.localPos().toPoint()))
        self.coordinateDisplay.setText("[" + str(int(pos.x())) + " mm, " + str(int(pos.y())) + " mm]")

        self.coordinateDisplay.setPos(self.GetCoordinateDisplayPoint(pos, self.coordinateDisplay.boundingRect()))

        horLine = QLineF(QPointF(self.stageRect.rect().left(), pos.y()),
                         QPointF(self.stageRect.rect().right(), pos.y()))
        vertLine = QLineF(QPointF(pos.x(), self.stageRect.rect().top()),
                          QPointF(pos.x(), self.stageRect.rect().bottom()))
        self.horLine.setLine(horLine)
        self.vertLine.setLine(vertLine)
        pen = QPen(QColor(255, 255, 255, 100))
        pen.setWidthF(1 / self.transform().m11())
        self.horLine.setPen(pen)
        self.vertLine.setPen(pen)

    def GetCoordinateDisplayPoint(self, position: QPointF, boundingRect: QRectF):
        centerPoint = self.stageRect.sceneBoundingRect().center()
        point = QPointF()
        offset = 10 / self.transform().m11()
        if position.x() < centerPoint.x():
            point.setX(position.x() + offset)
        else:
            point.setX(position.x() - boundingRect.width() - offset)

        if position.y() < centerPoint.y():
            point.setY(position.y() + offset)
        else:
            point.setY(position.y() - boundingRect.height() - offset)

        return point

    def UpdateItems(self, force=False):
        if not self.isVisible() and not force:
            return

        r = QRectF()
        r.setTopLeft(QPointF(self.stageSystem.xSettings.minimum, self.stageSystem.ySettings.minimum))
        r.setBottomRight(QPointF(self.stageSystem.xSettings.maximum, self.stageSystem.ySettings.maximum))

        self.stageRect.setRect(r)

        indicatorPosition = self.stageSystem.GetPosition()
        indicatorRect = QRectF()
        indicatorRect.setSize(QSizeF(10 / self.transform().m11(), 10 / self.transform().m11()))
        indicatorRect.moveCenter(QPointF(indicatorPosition[0], indicatorPosition[1]))
        self.indicator.setRect(indicatorRect)

        self.indicatorCoordinateDisplay.setText(
            "[" + str(int(indicatorPosition[0])) + " mm, " + str(int(indicatorPosition[1])) + " mm]")
        self.indicatorCoordinateDisplay.setPos(
            self.GetCoordinateDisplayPoint(QPointF(indicatorPosition[0],
                                                   indicatorPosition[1]),
                                           self.indicatorCoordinateDisplay.boundingRect()))

        horLine = QLineF(QPointF(r.left(), indicatorPosition[1]),
                         QPointF(r.right(), indicatorPosition[1]))
        vertLine = QLineF(QPointF(indicatorPosition[0], r.top()),
                          QPointF(indicatorPosition[0], r.bottom()))
        self.indicatorHorLine.setLine(horLine)
        self.indicatorVertLine.setLine(vertLine)

        if self.stageSystem.IsMoving():
            color = QColor(255, 128, 0)
        else:
            color = Qt.green

        self.indicator.setBrush(QBrush(color))
        self.indicatorCoordinateDisplay.setBrush(QBrush(color))
        pen = QPen(color)
        pen.setWidthF(1 / self.transform().m11())
        self.indicatorHorLine.setPen(pen)
        self.indicatorVertLine.setPen(pen)

        f = self.coordinateDisplay.font()
        f.setPixelSize(20 / (self.transform().m11()))
        self.coordinateDisplay.setFont(f)
        self.indicatorCoordinateDisplay.setFont(f)

        boundingRect = self.stageRect.rect()
        if self.sceneRect() != boundingRect:
            self.setSceneRect(boundingRect)
        self.stageRect.scale = self.transform().m11()

    def resizeEvent(self, event: QResizeEvent):
        self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)
        super().resizeEvent(event)
