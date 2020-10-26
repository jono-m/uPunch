from PySide2.QtWidgets import *
from Data.AlignmentCamera import *


class CameraViewer(QLabel):
    def __init__(self, camera: AlignmentCamera, fps: float):
        super().__init__()

        self.camera = camera

        self.setAlignment(Qt.AlignCenter)

        self.timer = QTimer()
        self.timer.timeout.connect(self.CaptureImage)
        self.timer.start(int(1000/fps))

    def CaptureImage(self):
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
