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

        self.stackedLayout = QStackedLayout()
        self.stackedLayout.addWidget(self.alignmentWidget)
        self.setLayout(self.stackedLayout)

        self.setModal(True)


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
        markLayout = QHBoxLayout()
        markLayout.addWidget(self.cameraViewer)
        markLayout.addLayout(buttonsLayout)
        layout = QVBoxLayout()
        layout.addWidget(self.stageViewer)
        layout.addLayout(markLayout)

        self.setLayout(layout)

    def MarkSpot(self, a: bool):
        image = self.cameraViewer.pixmap()
        pos = self.pjd.stageSystem.GetPosition()
        pos = QPointF(pos[0], pos[1])
        if a:
            self.aPreview.setPixmap(image)
            self.aSpot = pos
        else:
            self.bPreview.setPixmap(image)
            self.bSpot = pos

        self.pjd.design.globalA = self.aSpot
        self.pjd.design.globalB = self.bSpot

        self.designItem.CacheCircles()

    def Flip(self, checked: bool):
        self.pjd.design.flipY = bool(checked)

        self.designItem.CacheCircles()
