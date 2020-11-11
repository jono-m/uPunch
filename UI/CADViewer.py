from PySide2.QtWidgets import *
from PySide2.QtGui import *
from Data.Design import *
from Util import *


class CADViewer(QGraphicsView):
    def __init__(self, design: Design):
        super().__init__()

        self.setScene(QGraphicsScene(self))

        self.design = design

        self.gridSpacing = QSizeF(10, 10)

        self.setRenderHint(QPainter.Antialiasing, True)

        self._onBrush = QBrush(QColor(100, 255, 100, 255))
        self._offBrush = QBrush(QColor(255, 100, 100, 255))
        self._hoverPen = QPen(QColor(30, 30, 30))
        self._normalPen = QPen(QColor(30, 30, 30))

        self._circles: typing.Dict[Circle, QGraphicsEllipseItem] = {}

        self.setMouseTracking(True)

        self.legendWidget = LegendWidget()
        self.scene().addItem(self.legendWidget)

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
        itemsUnderMouse = self.scene().items(self.mapToScene(event.localPos().toPoint()))
        smallestCircle = None
        for itemUnderMouse in itemsUnderMouse:
            if itemUnderMouse in self._circles.values():
                circle = list(self._circles.keys())[list(self._circles.values()).index(itemUnderMouse)]
                if smallestCircle is None or circle.radius < smallestCircle.radius:
                    smallestCircle = circle

        self._hoverCircle = smallestCircle

        if self._hoverCircle is None:
            self.setCursor(Qt.ArrowCursor)
        else:
            self.setCursor(Qt.PointingHandCursor)

        self.Recolor()

    def mousePressEvent(self, event):
        if self._hoverCircle is not None:
            self._hoverCircle.specificallyIgnored = not self._hoverCircle.specificallyIgnored

        self.Recolor()

    def RefreshDesign(self):
        for c in self._circles.values():
            self.scene().removeItem(c)

        self._circles.clear()

        for c in self.design.GetLocalCircles():
            r = c.GetRect()
            r.moveCenter(QPointF(r.center().x(), -r.center().y()))
            self._circles[c] = self.scene().addEllipse(r, pen=Qt.NoPen)

        self.setSceneRect(self.design.rect)
        self.HandleResize()
        self.Recolor()

    def Recolor(self):
        for c in self._circles:
            if c.specificallyIgnored:
                self._circles[c].setBrush(self._offBrush)
            else:
                self._circles[c].setBrush(self._onBrush)

            if c == self._hoverCircle:
                self._circles[c].setPen(self._hoverPen)
            else:
                color = self._circles[c].brush().color().darker(150)
                self._normalPen.setColor(color)
                self._circles[c].setPen(self._normalPen)

            self._circles[c].setZValue(-c.radius)

    def HandleResize(self):
        self._hoverPen.setWidthF(2 / self.transform().m11())
        self._normalPen.setWidthF(1 / self.transform().m11())

        self.fitInView(ScaleRectCenter(self.sceneRect(), 1.2), Qt.KeepAspectRatio)

        if self.legendWidget is not None:
            self.legendWidget.setPos(self.mapToScene(QPoint(0, 0)))
            self.legendWidget.setScale(1/self.transform().m11())

    def resizeEvent(self, event):
        self.HandleResize()
        super().resizeEvent(event)


class LegendWidget(QGraphicsProxyWidget):
    def __init__(self):
        super().__init__()

        widget = QFrame()

        self.setWidget(widget)

        widget.setStyleSheet("""
        * {
        background-color: transparent;
        }
        QLabel {
        padding: 5px;
        }
        """)

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Legend:"))

        a = QLabel("To Punch")
        a.setAlignment(Qt.AlignCenter)
        a.setStyleSheet("""* {
        background-color: rgba(100, 255, 100, 255);
        font-weight: bold;
        }""")
        b = QLabel("Ignored")
        b.setAlignment(Qt.AlignCenter)
        b.setStyleSheet("""* {
        background-color: rgba(255, 100, 100, 255);
        font-weight: bold;
        }""")

        layout.addWidget(a)
        layout.addWidget(b)

        layout.setAlignment(Qt.AlignTop)

        layout.setSpacing(0)

        widget.setLayout(layout)

        widget.adjustSize()
