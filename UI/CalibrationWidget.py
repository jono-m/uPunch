from PySide2.QtWidgets import *
from Data.AlignmentCamera import *
from Data.StageSystem import *
from UI.CameraViewerWidget import *
from Data.CalibrationSettings import *
from UI.PunchTipsListWidget import *
from UI.StageViewerWidget import *


class CalibrationWidget(QFrame):
    def __init__(self, punchTips: PunchTips, calibrationSettings: CalibrationSettings, alignmentCamera: AlignmentCamera,
                 stageSystem: StageSystem):
        super().__init__()

        self.punchTips = punchTips
        self.calibrationSettings = calibrationSettings
        self.alignmentCamera = alignmentCamera
        self.stageSystem = stageSystem

        self.punchOffsetLabel = QLabel("Offset from camera to punch (mm): ")

        self.xLabel = QLabel("X: ")
        self.yLabel = QLabel("Y: ")
        self.xField = QDoubleSpinBox()
        self.xField.valueChanged.connect(self.UpdateCalibration)

        self.yField = QDoubleSpinBox()
        self.yField.valueChanged.connect(self.UpdateCalibration)

        self.calibrateButton = QPushButton("Recalibrate")

        self.calibrateButton.clicked.connect(self.BeginRecalibrate)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.setLayout(layout)

        layout.addWidget(self.punchOffsetLabel)

        xLayout = QHBoxLayout()
        yLayout = QHBoxLayout()
        xLayout.addWidget(self.xLabel)
        xLayout.addWidget(self.xField)
        yLayout.addWidget(self.yLabel)
        yLayout.addWidget(self.yField)

        layout.addLayout(xLayout)
        layout.addLayout(yLayout)
        layout.addWidget(self.calibrateButton)

        self.UpdateFields()

    def UpdateFields(self):
        for x in self.children():
            x.blockSignals(True)

        self.xField.setMinimum(self.stageSystem.xSettings.minimum)
        self.xField.setMaximum(self.stageSystem.xSettings.maximum)
        self.yField.setMinimum(self.stageSystem.ySettings.minimum)
        self.yField.setMaximum(self.stageSystem.ySettings.maximum)
        self.xField.setValue(self.calibrationSettings.punchOffset.x())
        self.yField.setValue(self.calibrationSettings.punchOffset.y())

        for x in self.children():
            x.blockSignals(False)

    def UpdateCalibration(self):
        self.calibrationSettings.punchOffset = QPointF(self.xField.value(), self.yField.value())

    def BeginRecalibrate(self):
        dialog = RecalibrateDialog(self, self.punchTips, self.calibrationSettings, self.alignmentCamera, self.stageSystem)
        dialog.finished.connect(self.UpdateFields)
        dialog.exec_()


class RecalibrateDialog(QDialog):
    def __init__(self, parent, punchTips: PunchTips, calibrationSettings: CalibrationSettings,
                 alignmentCamera: AlignmentCamera,
                 stageSystem: StageSystem):
        super().__init__(parent)

        self.calibrationSettings = calibrationSettings
        self.alignmentCamera = alignmentCamera
        self.stageSystem = stageSystem

        self.setWindowTitle("Camera-Punch Calibration")

        self.stackedLayout = QStackedLayout()
        self.setLayout(self.stackedLayout)

        self.ptsWidget = PunchTipSelection(punchTips)
        self.ptsWidget.OnCancel.Register(self.reject)
        self.ptsWidget.OnTipSelected.Register(self.SetPunchTipSelection)

        self.punchSpotWidget = PunchSpotMaker(self.stageSystem)
        self.punchSpotWidget.OnBack.Register(lambda: self.stackedLayout.setCurrentWidget(self.ptsWidget))
        self.punchSpotWidget.OnPunchFinished.Register(self.SetMarkPoint)

        self.cameraCalibrationWidget = CameraCalibrationWidget(self.alignmentCamera, self.stageSystem)
        self.cameraCalibrationWidget.OnBack.Register(lambda: self.stackedLayout.setCurrentWidget(self.punchSpotWidget))
        self.cameraCalibrationWidget.OnFinished.Register(self.SetCalibration)

        self.stackedLayout.addWidget(self.ptsWidget)
        self.stackedLayout.addWidget(self.punchSpotWidget)
        self.stackedLayout.addWidget(self.cameraCalibrationWidget)

        self.markPoint = QPointF()

        self.setModal(True)

    def SetPunchTipSelection(self, selectedTip: PunchTip):
        self.stackedLayout.setCurrentWidget(self.punchSpotWidget)
        self.punchSpotWidget.activeTip = selectedTip

    def SetMarkPoint(self):
        p = self.stageSystem.GetPosition()
        self.markPoint = QPointF(p[0], p[1])
        print(self.calibrationSettings.punchOffset)
        shifted = self.markPoint + self.calibrationSettings.punchOffset
        self.stageSystem.SetPosition(x=shifted.x(), y=shifted.y())

        self.stackedLayout.setCurrentWidget(self.cameraCalibrationWidget)

    def SetCalibration(self):
        p = self.stageSystem.GetPosition()
        shifted = QPointF(p[0], p[1])
        self.calibrationSettings.punchOffset = shifted - self.markPoint

        self.accept()


class PunchTipSelection(QFrame):
    def __init__(self, punchTips: PunchTips):
        super().__init__()
        self.OnCancel = Event()
        self.OnTipSelected = Event()

        self.punchTipsList = PunchTipsListWidget(punchTips)
        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.clicked.connect(self.OnCancel.Invoke)
        self.nextButton = QPushButton("Next")
        self.nextButton.clicked.connect(lambda: self.OnTipSelected.Invoke(self.punchTipsList.selectedTip))

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Attach and select a punch tip for calibration:"))
        layout.addWidget(self.punchTipsList)
        bLayout = QHBoxLayout()
        bLayout.setAlignment(Qt.AlignRight)
        bLayout.addWidget(self.cancelButton)
        bLayout.addWidget(self.nextButton)
        layout.addLayout(bLayout)

        self.setLayout(layout)

        self.OnTipSelected.Invoke(self.punchTipsList.selectedTip)


class PunchSpotMaker(QFrame):
    STATE_PREP = -1
    STATE_IDLE = 0
    STATE_PUNCH = 1
    STATE_RAISE = 2

    def __init__(self, stageSystem: StageSystem):
        super().__init__()

        self.stageSystem = stageSystem

        self.viewer = StageViewerWidget(stageSystem, False)

        self.OnBack = Event()
        self.OnPunchFinished = Event()

        self.backButton = QPushButton("Back")
        self.backButton.clicked.connect(self.OnBack.Invoke)
        self.punchButton = QPushButton("Punch")
        self.punchButton.clicked.connect(self.DoPunch)

        layout = QVBoxLayout()
        layout.addWidget(QLabel(
            "Move the tip above a clean reference position on the pad. Click 'Punch' to mark the position on the pad."))
        layout.addWidget(self.viewer)
        bLayout = QHBoxLayout()
        bLayout.setAlignment(Qt.AlignRight)
        bLayout.addWidget(self.backButton)
        bLayout.addWidget(self.punchButton)
        layout.addLayout(bLayout)

        self.setLayout(layout)

        self.activeTip: typing.Optional[PunchTip] = None

        self.RaisePunch()
        self.state = PunchSpotMaker.STATE_PREP

        timer = QTimer(self)
        timer.timeout.connect(self.Tick)
        timer.start()

    def DoPunch(self):
        self.state = PunchSpotMaker.STATE_PUNCH
        self.backButton.setEnabled(False)
        self.punchButton.setEnabled(False)
        self.punchButton.setText("Marking spot...")
        self.stageSystem.SetPosition(z=self.activeTip.punchDepth)

    def RaisePunch(self):
        self.state = PunchSpotMaker.STATE_RAISE
        self.punchButton.setEnabled(False)
        self.punchButton.setText("Raising...")
        self.stageSystem.SetPosition(z=self.stageSystem.zSettings.minimum)

    def Tick(self):
        if not self.stageSystem.IsMoving():
            if self.state == PunchSpotMaker.STATE_PREP or self.state == PunchSpotMaker.STATE_RAISE:
                self.punchButton.setEnabled(True)
                self.backButton.setEnabled(True)
                self.punchButton.setText("Punch")
                if self.state == PunchSpotMaker.STATE_RAISE:
                    self.OnPunchFinished.Invoke()
                self.state = PunchSpotMaker.STATE_IDLE
            elif self.state == PunchSpotMaker.STATE_PUNCH:
                self.RaisePunch()


class CameraCalibrationWidget(QFrame):
    def __init__(self, alignmentCamera: AlignmentCamera, stageSystem: StageSystem):
        super().__init__()
        self.alignmentCamera = alignmentCamera
        self.stageSystem = stageSystem

        self.OnBack = Event()
        self.OnFinished = Event()

        self.viewer = StageViewerWidget(stageSystem, False)
        self.cameraPreview = CameraViewerWidget(self.alignmentCamera, 30, True)
        self.cameraPreview.OnClicked.Register(self.CameraAdjust)

        self.backButton = QPushButton("Back")
        self.backButton.clicked.connect(self.OnBack.Invoke)
        self.finishButton = QPushButton("Finish")
        self.finishButton.clicked.connect(self.OnFinished.Invoke)

        layout = QVBoxLayout()
        layout.addWidget(QLabel(
            "Move the tip above a clean reference position on the pad. Click 'Punch' to mark the position on the pad."))

        tLayout = QHBoxLayout()
        tLayout.addWidget(self.viewer)
        tLayout.addWidget(self.cameraPreview)
        layout.addLayout(tLayout)

        bLayout = QHBoxLayout()
        bLayout.setAlignment(Qt.AlignRight)
        bLayout.addWidget(self.backButton)
        bLayout.addWidget(self.finishButton)
        layout.addLayout(bLayout)

        self.setLayout(layout)

    def CameraAdjust(self, offset: QPointF):
        currentPosition = self.stageSystem.GetPosition()
        xy = QPointF(currentPosition[0], currentPosition[1])
        final = xy+offset
        self.stageSystem.SetPosition(x=final.x(), y=final.y())