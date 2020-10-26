from UI.CameraSettingsWidget import *
from UI.PunchJobWidget import *
from UI.PunchTipsSettingsWidget import *
from UI.StageSettingsWidget import *
from StylesheetLoader import *
from Data.PunchTips import *
from PySide2.QtGui import *
from UI.CalibrationWidget import *
from Data.StageSystem import *
from Data.AlignmentCamera import *


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.stageSystem = StageSystem()
        self.alignmentCamera = AlignmentCamera()
        self.calibrationSettings = CalibrationSettings()
        self.punchTips = PunchTips()
        self.punchTips.tips.append(PunchTip("3mm tip", 0, 3))
        self.punchTips.tips.append(PunchTip("1.5mm tip", 0.2, 1.5))
        self.punchTips.tips.append(PunchTip("0.75mm tip", 0.5, .75))

        self.tabArea = QTabWidget()
        self.setCentralWidget(self.tabArea)
        self.tabArea.setTabPosition(QTabWidget.West)

        self.AddTab(PunchJobWidget(), "Punch Job")
        self.AddTab(PunchTipsSettingsWidget(self.punchTips), "Punch Tips")
        self.AddTab(CameraSettingsWidget(self.alignmentCamera), "Camera Settings")
        self.AddTab(StageSettingsWidget(self.stageSystem), "Stage Settings")
        self.AddTab(CalibrationWidget(self.calibrationSettings, self.alignmentCamera, self.stageSystem), "Calibration")
        StylesheetLoader.GetInstance().RegisterWidget(self)

        icon = QIcon("Assets/icon.png")
        self.setWindowIcon(icon)

        self.setWindowTitle("μPunch")

        self.tabArea.setCurrentIndex(1)

    def AddTab(self, widget, text):
        self.tabArea.addTab(widget, "")
        self.tabArea.tabBar().setTabButton(self.tabArea.count() - 1, QTabBar.LeftSide,
                                           QLabel(text, self.tabArea.tabBar()))

    def closeEvent(self, event:QCloseEvent):
        self.alignmentCamera.DisconnectCamera()