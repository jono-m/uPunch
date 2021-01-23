from PySide2.QtWidgets import *
from UI.StageViewerWidget import *
from UI.CameraViewerWidget import *
from Data.CalibrationSettings import *


class SwitchTipWindow(QDialog):
    def __init__(self, parent, stageSystem: StageSystem, camera: AlignmentCamera,
                 calibrationSettings: CalibrationSettings):
        super().__init__(parent)

        self._stageSystem = stageSystem
        self._alignmentCamera = camera
        self._calibrationSettings = calibrationSettings

        self.setModal(True)

        self.setWindowTitle("Switch Punch Tip")

        self.removalInstructions: typing.List[typing.Tuple[str, typing.Callable]] = \
            [("Press CONTINUE to move axis to tip loading position.", self.MoveToLoad),
             ("Unscrew the vise collar and remove the current tip.", None),
             ("Place the new tip into the vise and lightly tighten the vise collar.<br> "
              "<b>The tip should be inserted far enough to clear the stage.</b>", self.MoveToDot),
             ("Loosen the vise collar to rest the tip on the stage. <br>"
              "<b>DO NOT TIGHTEN. THE TIP SHOULD BE LOOSE.</b>", self.MoveToTighten),
             ("Firmly tighten the vise collar.<br>"
              "<b>Make sure that the tip is straight and touching the stage.</b>", self.RevealCalibration),
             ("Align the tip to the black dot on the stage.", self.MakeCalibration),
             ("Tip switch complete.", lambda: self.accept())]

        self.calibrationWidget = StageViewerWidget(self._stageSystem, False, True)
        self.calibrationWidget.setEnabled(False)
        self.removalLabel = QLabel()

        self.nextButton = QPushButton("CONTINUE")
        self.nextButton.clicked.connect(self.DoStep)

        layout = QVBoxLayout()
        layout.addWidget(self.removalLabel)
        layout.addWidget(self.nextButton)
        layout.addWidget(self.calibrationWidget)

        self.setLayout(layout)

        self.tickTimer = QTimer(self)
        self.tickTimer.timeout.connect(self.DoTick)
        self.tickTimer.start()

        self._step = 0

    def DoTick(self):
        moving = self._stageSystem.IsMoving()
        self.nextButton.setEnabled(not moving)

        if moving:
            self.removalLabel.setText("Please wait...")
        else:
            self.removalLabel.setText(self.removalInstructions[self._step][0])

    def DoStep(self):
        doneFunc = self.removalInstructions[self._step][1]
        if doneFunc is not None:
            doneFunc()

        self._step += 1

        if self._step >= len(self.removalInstructions):
            self.tickTimer.stop()
            return

    def MoveToLoad(self):
        self._stageSystem.MoveToLoadSpot()

    def MoveToDot(self):
        self._stageSystem.SetPosition(x=self._calibrationSettings.punchDotPosition.x(),
                                      y=self._calibrationSettings.punchDotPosition.y())

    def MoveToTighten(self):
        self._stageSystem.SetPosition(
            z=self._stageSystem.settings.punchDepth - self._stageSystem.settings.tipLoadingOffset)

    def RevealCalibration(self):
        self.calibrationWidget.setEnabled(True)

    def MakeCalibration(self):
        self._calibrationSettings.punchDotPosition = QPointF(self._stageSystem.GetPosition(self._stageSystem.xSettings),
                                                             self._stageSystem.GetPosition(self._stageSystem.ySettings))
