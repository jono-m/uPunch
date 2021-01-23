from PySide2.QtWidgets import *
from UI.CameraViewerWidget import *
from Data.CalibrationSettings import *
from UI.StageViewerWidget import *
from UI.CADGraphicsItem import *
from Data.Design import *
from UI.CADEditor import *


class PunchJobDialog(QDialog):
    def __init__(self, parent, design: Design, calibrationSettings: CalibrationSettings,
                 alignmentCamera: AlignmentCamera,
                 stageSystem: StageSystem):
        super().__init__(parent)
        self.design = design
        self.calibrationSettings = calibrationSettings
        self.alignmentCamera = alignmentCamera
        self.stageSystem = stageSystem

        self.setWindowTitle("Punch Job: " + self.design.filename)

        self.alignmentWidget = AlignmentWidget(self)
        self.alignmentWidget.OnCancel.Register(lambda: self.reject())
        self.alignmentWidget.OnStartJob.Register(self.StartJob)

        self.jobFollowWidget = JobFollowWidget(self)
        self.jobFollowWidget.OnCancel.Register(lambda: self.reject())
        self.jobFollowWidget.OnFinish.Register(lambda: self.accept())

        self.stackedLayout = QStackedLayout()
        self.stackedLayout.addWidget(self.alignmentWidget)
        self.stackedLayout.addWidget(self.jobFollowWidget)
        self.setLayout(self.stackedLayout)

        QApplication.processEvents()
        self.move(0, 0)
        self.setModal(True)

    def StartJob(self):
        self.stackedLayout.setCurrentWidget(self.jobFollowWidget)
        self.jobFollowWidget.StartJob()

    def GetPunch(self):
        return self.alignmentWidget.punchSelection.selectedTip


class AlignmentWidget(QFrame):
    def __init__(self, pjd: PunchJobDialog):
        super().__init__()

        self.pjd = pjd

        self.stageViewer = StageViewerWidget(self.pjd.stageSystem, False, False)

        self.cameraViewer = CameraViewerWidget(self.pjd.alignmentCamera, 30, True)
        self.cameraViewer.OnClicked.Register(self.pjd.stageSystem.MoveXY)

        self._aMarked = False
        self._bMarked = False
        self._dotMarked = False

        self.pjd.stageSystem.SetPosition(x=self.pjd.calibrationSettings.cameraDotPosition.x(),
                                         y=self.pjd.calibrationSettings.cameraDotPosition.x(),
                                         z=self.pjd.stageSystem.zSettings.minimum)

        self.markDot = QPushButton("Mark Calibration Dot")
        self.markDot.clicked.connect(self.MarkCalibration)
        self.markDot.setProperty("markDone", False)
        self.aMarkButton = QPushButton("Mark Position as A")
        self.aMarkButton.clicked.connect(lambda: self.MarkSpot(True))
        self.aMarkButton.setProperty("markDone", False)
        self.bMarkButton = QPushButton("Mark Position as B")
        self.bMarkButton.clicked.connect(lambda: self.MarkSpot(False))
        self.bMarkButton.setProperty("markDone", False)

        self.flipCheck = QCheckBox("Flip Design")
        self.flipCheck.setChecked(self.pjd.design.flipY)

        self.designWidget = CADEditor(self.pjd.design)
        self.designWidget.hideIgnored = True
        self.designWidget.setEnabled(False)
        self.designWidget.RefreshDesign()

        self.flipCheck.toggled.connect(self.Flip)

        self.aSpot = QPointF()
        self.bSpot = QPointF()

        self.OnCancel = Event()
        self.OnStartJob = Event()

        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.clicked.connect(self.OnCancel.Invoke)
        self.nextButton = QPushButton("Start Job")
        self.nextButton.clicked.connect(self.OnStartJob.Invoke)

        self.designItem = CADGraphicsItem(self.pjd.design)
        self.stageViewer.xyViewer.scene().addItem(self.designItem)

        alignLayout = QGridLayout()
        alignLayout.addWidget(self.cameraViewer, 0, 0, 1, 2)
        alignLayout.addWidget(self.markDot, 1, 0, 1, 2)
        alignLayout.addWidget(self.aMarkButton, 2, 0)
        alignLayout.addWidget(self.bMarkButton, 2, 1)

        buttonsLayout = QHBoxLayout()
        buttonsLayout.addWidget(self.flipCheck)
        buttonsLayout.addWidget(self.cancelButton)
        buttonsLayout.addWidget(self.nextButton)

        layout = QGridLayout()
        layout.addWidget(self.designWidget, 0, 0)
        layout.addWidget(self.stageViewer, 0, 1)
        layout.addLayout(alignLayout, 1, 0)
        layout.addLayout(buttonsLayout, 2, 0)

        self.setLayout(layout)

        self.CheckReady()

    def MarkCalibration(self):
        pos = self.pjd.stageSystem.GetPosition()
        self.pjd.calibrationSettings.cameraDotPosition = QPointF(pos[0], pos[1])
        self._dotMarked = True
        self.markDot.setProperty("markDone", True)
        self.markDot.setStyle(self.markDot.style())
        self.CheckReady()

    def MarkSpot(self, a: bool):
        pos = self.pjd.stageSystem.GetPosition()
        pos = QPointF(pos[0], pos[1])
        if a:
            self.aSpot = pos
            self._aMarked = True
            self.aMarkButton.setProperty("markDone", True)
            self.aMarkButton.setStyle(self.aMarkButton.style())
        else:
            self.bSpot = pos
            self._bMarked = True
            self.bMarkButton.setProperty("markDone", True)
            self.bMarkButton.setStyle(self.bMarkButton.style())

        self.pjd.design.globalA = self.aSpot
        self.pjd.design.globalB = self.bSpot

        self.designItem.CacheCircles()

        self.CheckReady()

    def CheckReady(self):
        if self._aMarked and self._bMarked and self._dotMarked:
            self.nextButton.setEnabled(True)
        else:
            self.nextButton.setEnabled(False)

    def Flip(self, checked: bool):
        self.pjd.design.flipY = bool(checked)

        self.designItem.CacheCircles()


class JobFollowWidget(QFrame):
    def __init__(self, pjd: PunchJobDialog):
        super().__init__()

        self.pjd = pjd

        self.stageViewer = StageViewerWidget(self.pjd.stageSystem, False)
        self.stageViewer.setEnabled(False)

        self.OnFinish = Event()
        self.OnCancel = Event()

        self.designItem = CADGraphicsItem(self.pjd.design)
        self.stageViewer.xyViewer.scene().addItem(self.designItem)

        self.stageViewer.setEnabled(False)

        self.pjd.stageSystem.OnPunchFinish.Register(self.PunchFinished)
        self.pjd.stageSystem.OnPanFinish.Register(self.PanFinished)

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
        self.designItem.setPos(self.pjd.calibrationSettings.CameraToPunch(QPointF(0, 0)))
        self.circlesToPunch = [c for c in self.pjd.design.GetAlignedCircles() if not c.specificallyIgnored]
        for c in self.circlesToPunch:
            c.center = self.pjd.calibrationSettings.CameraToPunch(c.center)
        self.isInJob = True
        self.currentCircleNumber = -1
        self.PunchFinished()

    def CancelJob(self):
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
        self.pjd.stageSystem.SetPosition(x=pos.x(), y=pos.y())

    def PanFinished(self):
        if not self.isInJob:
            return
        self.pjd.stageSystem.DoPunch()
