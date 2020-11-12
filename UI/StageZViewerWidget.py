from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
from Data.StageSystem import *
from UI.StageRectGraphicsItem import *


class StageZViewerWidget(QGraphicsView):
    def __init__(self, stageSystem: StageSystem, controllable=True):
        super().__init__()

        self.stageSystem = stageSystem

        self.OnClicked = Event()

        self.setBackgroundBrush(QBrush(QColor(100, 100, 100)))

        self.setScene(QGraphicsScene())

        self.stageRect = StageRectGraphicsItem()
        self.stageRect.showX = False
        self.scene().addItem(self.stageRect)
        self.indicator = self.scene().addEllipse(QRect(), Qt.NoPen, QBrush(QColor(255, 0, 0)))

        self.indicatorCoordinateDisplay = self.scene().addSimpleText("")
        self.indicatorHorLine = self.scene().addLine(QLineF())

        self.coordinateDisplay = self.scene().addSimpleText("")
        self.coordinateDisplay.setBrush(QBrush(Qt.white))
        self.horLine = self.scene().addLine(QLineF(), QPen(Qt.white))

        self.setFixedWidth(100)
        self.setMinimumHeight(300)

        self.timer = QTimer()
        self.timer.timeout.connect(self.UpdateItems)
        self.timer.start(30)

        self.setMouseTracking(True)

        self.setEnabled(controllable)

        self.UpdateItems(True)

    def enterEvent(self, event: QEvent):
        if self.isEnabled():
            self.coordinateDisplay.setVisible(True)
            self.horLine.setVisible(True)
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent):
        self.coordinateDisplay.setVisible(False)
        self.horLine.setVisible(False)
        super().leaveEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        if self.isEnabled():
            axisPos = self.stageSystem.zSettings.ClampAxis(
                self.StageToAxis(self.mapToScene(event.localPos().toPoint()).y()))
            self.OnClicked.Invoke(axisPos)
            self.setCursor(Qt.ArrowCursor)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.isEnabled() and not self.stageSystem.IsMoving():
            self.setCursor(Qt.PointingHandCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

        axisPos = self.stageSystem.zSettings.ClampAxis(
            self.StageToAxis(self.mapToScene(event.localPos().toPoint()).y()))
        stagePos = self.AxisToStage(axisPos)
        self.coordinateDisplay.setText("[" + str(int(axisPos)) + "mm]")
        self.coordinateDisplay.setPos(QPointF((self.width() - self.coordinateDisplay.boundingRect().width()),
                                              stagePos - self.coordinateDisplay.boundingRect().height() - 20 /
                                              self.transform().m11()))
        horLine = QLineF(QPointF(self.stageRect.rect().left(), stagePos),
                         QPointF(self.stageRect.rect().right(), stagePos))
        self.horLine.setLine(horLine)

    def UpdateItems(self, force=False):
        if not self.isVisible() and not force:
            return

        r = QRectF()
        r.setTopLeft(QPointF(0, 0))
        r.setBottomRight(QPointF(self.width(), self.height()))

        self.stageRect.setRect(r)

        indicatorPosition = self.stageSystem.GetPosition()
        indicatorRect = QRectF()
        indicatorRect.setSize(QSizeF(r.size().width() / 10, r.size().width() / 10))
        indicatorRect.moveCenter(
            QPointF(self.width() / 2, self.AxisToStage(indicatorPosition[2])))
        self.indicator.setRect(indicatorRect)

        self.indicatorCoordinateDisplay.setText("[" + str(int(indicatorPosition[2])) + "mm]")
        self.indicatorCoordinateDisplay.setPos(
            QPointF((self.width() - self.indicatorCoordinateDisplay.boundingRect().width()),
                    indicatorRect.center().y() - self.indicatorCoordinateDisplay.boundingRect().height() - 20 /
                    self.transform().m11()))
        horLine = QLineF(QPointF(r.left(), indicatorRect.center().y()),
                         QPointF(r.right(), indicatorRect.center().y()))
        self.indicatorHorLine.setLine(horLine)

        if self.stageSystem.IsMoving():
            color = QColor(255, 128, 0)
        else:
            color = Qt.green

        self.indicator.setBrush(QBrush(color))
        self.indicatorCoordinateDisplay.setBrush(QBrush(color))
        self.indicatorHorLine.setPen(QPen(color))

        self.stageRect.lineSpacing = self.AxisToStage(10)

        f = self.coordinateDisplay.font()
        f.setPixelSize(20 / (self.transform().m11()))
        self.coordinateDisplay.setFont(f)
        self.indicatorCoordinateDisplay.setFont(f)

        viewRect = self.stageRect.rect().marginsAdded(QMarginsF(0, 50, 0, 0)/self.transform().m11())
        if viewRect != self.sceneRect():
            self.stageRect.scale = self.transform().m11()
            self.setSceneRect(viewRect)

    def StageToAxis(self, pt: float):
        return (pt / self.stageRect.rect().height()) * \
               (self.stageSystem.zSettings.maximum - self.stageSystem.zSettings.minimum) + \
               self.stageSystem.zSettings.minimum

    def AxisToStage(self, pt: float):
        return (pt - self.stageSystem.zSettings.minimum) / \
               (self.stageSystem.zSettings.maximum - self.stageSystem.zSettings.minimum) * \
               self.stageRect.rect().height()

    def resizeEvent(self, event: QResizeEvent):
        self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)
        super().resizeEvent(event)
