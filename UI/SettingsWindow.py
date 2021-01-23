from PySide2.QtWidgets import *
from UI.CameraSettingsWidget import *
from UI.StageSettingsWidget import *


class SettingsWindow(QDialog):
    def __init__(self, parent, camera: AlignmentCamera, stageSystem: StageSystem):
        super().__init__(parent)

        self._camera = camera
        self._stageSystem = stageSystem

        self.tabArea = QTabWidget()
        self.tabArea.setTabPosition(QTabWidget.TabPosition.West)

        cameraSettings = CameraSettingsWidget(camera)
        self.AddTab(cameraSettings, "Camera")

        stageSettings = StageSettingsWidget(stageSystem)
        self.AddTab(stageSettings, "Stage")

        self.setWindowTitle("Settings")

        layout = QVBoxLayout()
        layout.addWidget(self.tabArea)
        self.setLayout(layout)

        self.setModal(True)

    def AddTab(self, widget, text):
        self.tabArea.addTab(widget, "")
        self.tabArea.tabBar().setTabButton(self.tabArea.count() - 1, QTabBar.LeftSide,
                                           QLabel(text, self.tabArea.tabBar()))
