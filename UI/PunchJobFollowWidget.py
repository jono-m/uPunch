from PySide2.QtWidgets import *
from UI.CameraViewerWidget import *
from Data.CalibrationSettings import *
from UI.StageViewerWidget import *
from UI.CADGraphicsItem import *
from Data.Design import *
from UI.CADEditor import *


class PunchJobFollowWidget(QFrame):
    def __init__(self, design: Design, calibrationSettings: CalibrationSettings,
                 alignmentCamera: AlignmentCamera,
                 stageSystem: StageSystem):
        super().__init__()

        self.design = design
        self.calibrationSettings = calibrationSettings
        self.alignmentCamera = alignmentCamera
        self.stageSystem = stageSystem

        self.stageViewer = StageViewerWidget(self.stageSystem, False)
        self.stageViewer.setEnabled(False)

        self.OnFinish = Event()
        self.OnCancel = Event()

        self.designItem = CADGraphicsItem(self.design)
        self.stageViewer.xyViewer.scene().addItem(self.designItem)

        self.stageViewer.setEnabled(False)

        self.stageSystem.OnPunchFinish.Register(self.PunchFinished)
        self.stageSystem.OnPanFinish.Register(self.PanFinished)

        self.isInJob = False

        self.currentCircleNumber = -1

        self.circlesToPunch: typing.List[Circle] = []

        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.clicked.connect(self.CancelJob)

        layout = QVBoxLayout()
        layout.addWidget(self.stageViewer)
        buttons = QHBoxLayout()
        buttons.addWidget(self.cancelButton)
        layout.addLayout(buttons)

        self.setLayout(layout)

    def StartJob(self):
        self.designItem.CacheCircles()
        self.designItem.setPos(self.calibrationSettings.CameraToPunch(QPointF(0, 0)))
        self.circlesToPunch = [c for c in self.design.GetAlignedCircles() if not c.specificallyIgnored]
        for c in self.circlesToPunch:
            c.center = self.calibrationSettings.CameraToPunch(c.center)
        self.SortCircles()
        self.isInJob = True
        self.currentCircleNumber = -1
        self.PunchFinished()

    def SortCircles(self):
        pass

    def CancelJob(self):
        quest = QMessageBox.question(self, "Confirm", "Are you sure you want to cancel?")
        if quest == QMessageBox.Yes:
            self.isInJob = False
            self.OnCancel.Invoke()

    def PunchFinished(self):
        if not self.isInJob:
            return

        self.currentCircleNumber += 1

        if self.currentCircleNumber >= len(self.circlesToPunch):
            self.isInJob = False
            self.OnFinish.Invoke()
            return

        pos = self.circlesToPunch[self.currentCircleNumber].center
        self.stageSystem.SetPosition(x=pos.x(), y=pos.y())

    def PanFinished(self):
        if not self.isInJob:
            return
        self.stageSystem.DoPunch()
