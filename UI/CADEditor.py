from PySide2.QtWidgets import *
from PySide2.QtGui import *
from Data.Design import *
from Util import *


class CADEditor(QGraphicsView):
    def __init__(self, design: Design):
        super().__init__()

        self.setScene(QGraphicsScene(self))

        self.OnCircleClicked = Event()

        self.CanHoverFunc: typing.Callable[[Circle], bool] = lambda c: True

        self.design = design

        self.gridSpacing = QSizeF(10, 10)

        self.setRenderHint(QPainter.Antialiasing, True)

        self._onBrush = QBrush(QColor(100, 255, 100, 255))
        self._offBrush = QBrush(QColor(255, 100, 100, 255))
        self._highlightBrush = QBrush(QColor(150, 150, 255, 255))
        self._hoverPen = QPen(QColor(30, 30, 30))
        self._normalPen = QPen(QColor(30, 30, 30))

        self.highlightCircle: typing.Optional[Circle] = None

        self._circles: typing.Dict[Circle, QGraphicsEllipseItem] = {}

        self.setMouseTracking(True)

        self.hideIgnored = False

        self._hoverCircle: typing.Optional[Circle] = None

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)

        pen = QPen()
        pen.setColor(QColor(240, 240, 240))
        pen.setWidthF(1 / self.transform().m11())
        painter.setPen(pen)

        if self.gridSpacing.width() > 0:
            xStart = rect.left() - rect.left() % self.gridSpacing.width()
            while xStart <= rect.right():
                painter.drawLine(int(xStart), int(rect.bottom()), int(xStart), int(rect.top()))
                xStart = xStart + self.gridSpacing.width()

        if self.gridSpacing.height() > 0:
            yStart = rect.top() - rect.top() % self.gridSpacing.height()
            while yStart <= rect.bottom():
                painter.drawLine(int(rect.left()), int(yStart), int(rect.right()), int(yStart))
                yStart = yStart + self.gridSpacing.height()

    def mouseMoveEvent(self, event: QMouseEvent):
        if not self.isEnabled():
            return
        itemsUnderMouse = self.scene().items(self.mapToScene(event.localPos().toPoint()))
        self._hoverCircle = None
        for itemUnderMouse in itemsUnderMouse:
            if itemUnderMouse in self._circles.values():
                circle = list(self._circles.keys())[list(self._circles.values()).index(itemUnderMouse)]
                if self.CanHoverFunc(circle):
                    self._hoverCircle = circle
                    break

        if self._hoverCircle is None:
            self.setCursor(Qt.ArrowCursor)
        else:
            self.setCursor(Qt.PointingHandCursor)

        self.Recolor()

    def mousePressEvent(self, event):
        if not self.isEnabled():
            return
        if self._hoverCircle is not None:
            self.OnCircleClicked.Invoke(self._hoverCircle)

        self.Recolor()

    def RefreshDesign(self):
        for c in self._circles.values():
            self.scene().removeItem(c)

        self._circles.clear()

        bRect = None

        for c in self.design.GetLocalCircles():
            if self.hideIgnored:
                if c.specificallyIgnored:
                    continue
            r = c.GetRect()
            r.moveCenter(QPointF(r.center().x(), -r.center().y()))
            if bRect is None:
                bRect = r
            else:
                bRect = bRect.united(r)
            self._circles[c] = self.scene().addEllipse(r)

        if bRect is None:
            bRect = self.sceneRect()
        self.setSceneRect(bRect)
        self.HandleResize()
        self.Recolor()

    def Recolor(self):
        for c in self._circles:
            if c.specificallyIgnored:
                self._circles[c].setBrush(self._offBrush)
            else:
                self._circles[c].setBrush(self._onBrush)

            if c == self.highlightCircle:
                self._circles[c].setBrush(self._highlightBrush)

            if c == self._hoverCircle:
                self._circles[c].setPen(self._hoverPen)
            else:
                color = self._circles[c].brush().color().darker(150)
                self._normalPen.setColor(color)
                self._circles[c].setPen(self._normalPen)

    def HandleResize(self):
        self.fitInView(ScaleRectCenter(self.sceneRect(), 1.2), Qt.KeepAspectRatio)

        self._hoverPen.setWidthF(2 / self.transform().m11())
        self._normalPen.setWidthF(1 / self.transform().m11())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.HandleResize()
        self.Recolor()