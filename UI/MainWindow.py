from UI.CameraSettingsWidget import *
from UI.PunchJobSetupWidget import *
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

        self.welcomeLabel = QLabel("Welcome to μPunch.")
        self.welcomeLabel.setAlignment(Qt.AlignCenter)
        self.openButton = QPushButton(u"\U0001F5C1" + "\nOpen CAD... ")
        self.openButton.clicked.connect(self.PromptOpen)

        self.punchJobWidget = PunchJobSetupWidget(self.calibrationSettings, self.alignmentCamera, self.stageSystem)
        self.punchJobWidget.setVisible(False)

        self.switchTipButton = QPushButton(u"\U0001F5D8" + "\nSwitch Tip ")
        self.switchTipButton.clicked.connect(self.OpenSwitchTipWindow)
        self.settingsButton = QPushButton(u"\U0001F512" + "\nSettings")
        self.settingsButton.clicked.connect(self.OpenSettingsWindow)

        menuLayout = QHBoxLayout()
        menuLayout.setAlignment(Qt.AlignRight)
        menuLayout.addWidget(self.openButton)
        menuLayout.addWidget(self.switchTipButton)
        menuLayout.addWidget(self.settingsButton)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.welcomeLabel)
        mainLayout.addLayout(menuLayout)
        mainLayout.addWidget(self.punchJobWidget)

        self.mainWidget.setLayout(mainLayout)

        StylesheetLoader.GetInstance().RegisterWidget(self)

        icon = QIcon("Assets/icon.png")
        self.setWindowIcon(icon)

        self.setWindowTitle("μPunch")

        self.adjustSize()
        self.setFixedSize(self.size())

    def PromptOpen(self):
        if self.punchJobWidget.BrowseForDXF():
            self.openButton.setVisible(False)
            self.welcomeLabel.setVisible(False)
            self.punchJobWidget.setVisible(True)
            self.setFixedSize(QSize(16777215,16777215))
            self.resize(1200, 900)
            self.setMinimumSize(1200, 900)

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
