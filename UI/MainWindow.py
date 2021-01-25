from UI.CameraSettingsWidget import *
from UI.PunchJobSetupWidget import *
from UI.PunchJobAlignmentWidget import *
from UI.PunchJobFollowWidget import *
from UI.StageSettingsWidget import *
from StylesheetLoader import *
from PySide2.QtGui import *
from Data.StageSystem import *
from Data.MockStageSystem import *
from UI.SwitchTipWindow import *
from UI.SettingsWindow import *
from Data.Design import *
from Data.AlignmentCamera import *


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.stageSystem = MockStageSystem(self)
        self.alignmentCamera = AlignmentCamera()
        self.calibrationSettings = CalibrationSettings()

        self.mainWidget = QFrame()
        self.setCentralWidget(self.mainWidget)

        self.punchJobWidget = PunchJobSetupWidget(self.calibrationSettings, self.alignmentCamera, self.stageSystem)
        self.punchJobWidget.OnNext.Register(self.GoToAlignment)

        self.punchJobAlignmentWidget = PunchJobAlignmentWidget(self.punchJobWidget.design, self.calibrationSettings,
                                                               self.alignmentCamera, self.stageSystem)
        self.punchJobAlignmentWidget.OnCancel.Register(lambda: self.jobLayout.setCurrentIndex(0))
        self.punchJobAlignmentWidget.OnNext.Register(self.GoToJob)

        self.punchJobFollowWidget = PunchJobFollowWidget(self.punchJobWidget.design, self.calibrationSettings,
                                                         self.alignmentCamera, self.stageSystem)
        self.punchJobFollowWidget.OnCancel.Register(lambda: self.jobLayout.setCurrentIndex(0))
        self.punchJobFollowWidget.OnFinish.Register(lambda: self.jobLayout.setCurrentIndex(0))

        self.switchTipButton = QPushButton(u"\U0001F5D8" + "\nSwitch Tip ")
        self.switchTipButton.clicked.connect(self.OpenSwitchTipWindow)
        self.settingsButton = QPushButton(u"\U0001F512" + "\nSettings")
        self.settingsButton.clicked.connect(self.OpenSettingsWindow)

        menuLayout = QHBoxLayout()
        menuLayout.setAlignment(Qt.AlignRight)
        menuLayout.addWidget(self.switchTipButton)
        menuLayout.addWidget(self.settingsButton)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(menuLayout)

        self.jobLayout = QStackedLayout()
        self.jobLayout.addWidget(self.punchJobWidget)
        self.jobLayout.addWidget(self.punchJobAlignmentWidget)
        self.jobLayout.addWidget(self.punchJobFollowWidget)
        self.jobLayout.setCurrentIndex(0)

        mainLayout.addLayout(self.jobLayout)
        self.mainWidget.setLayout(mainLayout)

        self.setMinimumSize(1600, 900)

        StylesheetLoader.GetInstance().RegisterWidget(self)

        icon = QIcon("Assets/icon.png")
        self.setWindowIcon(icon)

        self.setWindowTitle("μPunch")

        timer = QTimer(self)
        timer.timeout.connect(self.Tick)
        timer.start()

    def Tick(self):
        self.switchTipButton.setVisible(self.jobLayout.currentIndex() == 0)
        self.settingsButton.setVisible(self.jobLayout.currentIndex() == 0)

    def GoToAlignment(self):
        self.punchJobAlignmentWidget.Begin()
        self.jobLayout.setCurrentIndex(1)

    def GoToJob(self):
        self.punchJobFollowWidget.StartJob()
        self.jobLayout.setCurrentIndex(2)

    def OpenSwitchTipWindow(self):
        switchTipWindow = SwitchTipWindow(self, self.stageSystem, self.alignmentCamera, self.calibrationSettings)
        switchTipWindow.exec_()

    def OpenSettingsWindow(self):
        (text, go) = QInputDialog.getText(self, "Password", "Enter Password", QLineEdit.EchoMode.Password)
        if go:
            if text == "nfkb":
                settingsWindow = SettingsWindow(self, self.alignmentCamera, self.stageSystem)
                settingsWindow.exec_()
            else:
                QMessageBox.critical(self, "Wrong Password", "Incorrect password.")

    def closeEvent(self, event: QCloseEvent):
        self.stageSystem.SaveSettings()
        self.alignmentCamera.SaveSettings()
        self.calibrationSettings.SaveSettings()
        self.alignmentCamera.DisconnectCamera()
