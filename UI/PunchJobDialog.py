from PySide2.QtWidgets import *
from UI.CameraViewerWidget import *
from Data.CalibrationSettings import *
from UI.PunchTipsListWidget import *
from UI.StageViewerWidget import *
from UI.CADGraphicsItem import *
from Data.Design import *


class PunchJobDialog(QDialog):
    def __init__(self, parent, design: Design, punchTips: PunchTips, calibrationSettings: CalibrationSettings,
                 alignmentCamera: AlignmentCamera,
                 stageSystem: StageSystem):
        super().__init__(parent)
        self.design = design
        self.punchTips = punchTips
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

        self.stageViewer = StageViewerWidget(self.pjd.stageSystem, False)

        self.cameraViewer = CameraViewerWidget(self.pjd.alignmentCamera, 30, True)
        self.cameraViewer.OnClicked.Register(self.pjd.stageSystem.MoveXY)

        self.aMarkButton = QPushButton("Mark Position as A")
        self.aMarkButton.clicked.connect(lambda: self.MarkSpot(True))
        self.bMarkButton = QPushButton("Mark Position as B")
        self.bMarkButton.clicked.connect(lambda: self.MarkSpot(False))

        self.flipCheck = QCheckBox("Flip Design")
        self.flipCheck.setChecked(self.pjd.design.flipY)

        self.flipCheck.toggled.connect(self.Flip)

        self.aPreview = QLabel()
        self.bPreview = QLabel()

        self.aSpot = QPointF()
        self.bSpot = QPointF()

        self.OnCancel = Event()
        self.OnStartJob = Event()

        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.clicked.connect(self.OnCancel.Invoke)
        self.nextButton = QPushButton("Start Job")
        self.nextButton.clicked.connect(self.OnStartJob.Invoke)

        self.punchSelection = PunchTipsListWidget(self.pjd.punchTips)

        self.designItem = CADGraphicsItem(self.pjd.design)
        self.stageViewer.xyViewer.scene().addItem(self.designItem)

        buttonsLayout = QVBoxLayout()
        buttonsLayout.addWidget(self.aPreview)
        buttonsLayout.addWidget(self.aMarkButton)
        buttonsLayout.addWidget(self.bPreview)
        buttonsLayout.addWidget(self.bMarkButton)
        buttonsLayout.addWidget(self.flipCheck)
        buttonsLayout.addWidget(self.cancelButton)
        buttonsLayout.addWidget(self.nextButton)
        markLayout = QHBoxLayout()
        markLayout.addWidget(self.cameraViewer)
        markLayout.addLayout(buttonsLayout)
        markLayout.addWidget(self.punchSelection)
        layout = QVBoxLayout()
        layout.addWidget(self.stageViewer)
        layout.addLayout(markLayout)

        self.setLayout(layout)

    def MarkSpot(self, a: bool):
        image = self.cameraViewer.pixmap()
        pos = self.pjd.stageSystem.GetPosition()
        pos = QPointF(pos[0], pos[1])
        if a:
            self.aPreview.setPixmap(image.scaled(256, 256, Qt.KeepAspectRatio))
            self.aSpot = pos
        else:
            self.bPreview.setPixmap(image.scaled(256, 256, Qt.KeepAspectRatio))
            self.bSpot = pos

        self.pjd.design.globalA = self.aSpot
        self.pjd.design.globalB = self.bSpot

        self.designItem.CacheCircles()

    def Flip(self, checked: bool):
        self.pjd.design.flipY = bool(checked)

        self.designItem.CacheCircles()


class JobFollowWidget(QFrame):
    def __init__(self, pjd: PunchJobDialog):
        super().__init__()

        self.pjd = pjd

        self.stageViewer = StageViewerWidget(self.pjd.stageSystem, False)

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
        self.circlesToPunch = self.pjd.design.GetAlignedCircles()
        for c in self.circlesToPunch:
            c.center = c.center + self.pjd.calibrationSettings.punchOffset
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
        self.pjd.stageSystem.DoPunch(self.pjd.GetPunch().punchDepth)
