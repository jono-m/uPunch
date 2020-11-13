from PySide2.QtWidgets import *
from Data.AlignmentCamera import *


class CameraViewerWidget(QLabel):
    def __init__(self, camera: AlignmentCamera, fps: float, showCrosshairs=True):
        super().__init__()

        self.camera = camera

        self.setAlignment(Qt.AlignCenter)

        self.timer = QTimer()
        self.timer.timeout.connect(self.CaptureImage)
        self.timer.start(int(1000 / fps))

        self.OnClicked = Event()

        self.showCrosshairs = showCrosshairs

        self.mouseIndicatorVisible = False

        self.mouseIndicatorPosition = QPointF()

        self.setMouseTracking(True)

    def enterEvent(self, event: QEvent):
        self.mouseIndicatorVisible = True

    def leaveEvent(self, event: QEvent):
        self.mouseIndicatorVisible = False

    def mouseMoveEvent(self, ev: QMouseEvent):
        self.mouseIndicatorPosition = ev.localPos()

        self.update()

    def mousePressEvent(self, ev: QMouseEvent):
        if self.showCrosshairs:
            clickPoint = ev.localPos() - QPointF(self.rect().width(), self.rect().height()) / 2
            scaled = clickPoint * self.camera.MillimetersPerPixel()
            self.OnClicked.Invoke(scaled)

    def paintEvent(self, arg__1: QPaintEvent):
        if not self.isVisible():
            return

        super().paintEvent(arg__1)

        painter = QPainter(self)

        crosshairPen = QPen(QColor(255, 255, 255))
        crosshairPen.setWidth(1)

        indicatorPen = QPen(QColor(255, 0, 0))
        indicatorPen.setWidth(1)

        painter.setPen(crosshairPen)
        painter.setBrush(Qt.NoBrush)

        if self.showCrosshairs:
            painter.drawLine(QPointF(self.rect().left(), self.rect().center().y()),
                             QPointF(self.rect().right(), self.rect().center().y()))
            painter.drawLine(QPointF(self.rect().center().x(), self.rect().top()),
                             QPointF(self.rect().center().x(), self.rect().bottom()))

            if self.mouseIndicatorVisible:
                painter.setPen(indicatorPen)
                painter.drawLine(QPointF(self.rect().left(), self.mouseIndicatorPosition.y()),
                                 QPointF(self.rect().right(), self.mouseIndicatorPosition.y()))
                painter.drawLine(QPointF(self.mouseIndicatorPosition.x(), self.rect().top()),
                                 QPointF(self.mouseIndicatorPosition.x(), self.rect().bottom()))

    def CaptureImage(self):
        if not self.isVisible():
            return

        image = self.camera.GetImage()
        if image is not None:
            self.setFixedSize(self.camera.GetResolution())
            self.setPixmap(QPixmap.fromImage(image))
        else:
            self.setMinimumSize(QSize(200, 200))
            self.setPixmap(None)
            self.setText("No camera selected.")

    def closeEvent(self, event: QCloseEvent):
        self.timer.stop()
