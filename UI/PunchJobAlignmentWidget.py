from PySide2.QtWidgets import *
from UI.CameraViewerWidget import *
from Data.CalibrationSettings import *
from UI.StageViewerWidget import *
from UI.CADGraphicsItem import *
from Data.Design import *
from UI.CADEditor import *


class PunchJobAlignmentWidget(QFrame):
    STATE_MARK_DOT = 0
    STATE_SELECT_FIRST = 1
    STATE_MARK_FIRST = 2
    STATE_SELECT_SECOND = 3
    STATE_MARK_SECOND = 4
    STATE_CONFIRM_DESIGN = 5

    instructionText = ["Align the camera to the calibration dot on the stage.",
                       "Select the first point to be used for alignment.",
                       "Align the camera to the first point.",
                       "Select the second point to be used for alignment.",
                       "Align the camera to the second point.",
                       "Confirm the alignment settings."]

    def __init__(self, design: Design, calibrationSettings: CalibrationSettings,
                 alignmentCamera: AlignmentCamera,
                 stageSystem: StageSystem):
        super().__init__()

        self.design = design
        self.calibrationSettings = calibrationSettings
        self.alignmentCamera = alignmentCamera
        self.stageSystem = stageSystem

        self.stageViewer = StageViewerWidget(self.stageSystem, False, False)
        self.cameraViewer = CameraViewerWidget(self.alignmentCamera, 30, True)
        self.cameraViewer.OnClicked.Register(self.stageSystem.MoveXY)

        self.OnNext = Event()
        self.OnCancel = Event()

        self.cadViewer = CADEditor(self.design)
        self.cadViewer.hideIgnored = True
        self.cadViewer.OnCircleClicked.Register(self.HandleCircleClick)

        self.instructionsText = QLabel("")
        self.instructionsText.setProperty("IsInstructions", True)
        self.markButton = QPushButton("Mark Position")
        self.markButton.clicked.connect(self.MarkPosition)
        self.startButton = QPushButton("Start")
        self.startButton.clicked.connect(lambda: self.OnNext.Invoke())
        self.cancelButton = QPushButton("Cancel Alignment")
        self.cancelButton.clicked.connect(lambda: self.OnCancel.Invoke())

        self.ignoreRotCheck = QCheckBox("Ignore rotation")
        self.ignoreRotCheck.setChecked(self.design.ignoreRotation)
        self.ignoreRotCheck.toggled.connect(self.IgnoreRotation)

        self.ignoreScaleCheck = QCheckBox("Ignore scale")
        self.ignoreScaleCheck.setChecked(self.design.ignoreScale)
        self.ignoreScaleCheck.toggled.connect(self.IgnoreScale)

        self.flipCheck = QCheckBox("Flip design (if features are on top)")
        self.flipCheck.setChecked(self.design.flipY)
        self.flipCheck.toggled.connect(self.Flip)

        self.alignmentDisplay = QLabel("")

        self.designItem = CADGraphicsItem(self.design)
        self.stageViewer.xyViewer.scene().addItem(self.designItem)

        self.state = PunchJobAlignmentWidget.STATE_MARK_DOT

        layout = QVBoxLayout()

        layout.addWidget(self.instructionsText)

        layout.addWidget(self.cadViewer, stretch=1)
        self.stageCamWidget = QFrame()
        stageCamLayout = QHBoxLayout()
        self.stageCamWidget.setLayout(stageCamLayout)
        stageCamLayout.addWidget(self.stageViewer)
        stageCamLayout.addWidget(self.cameraViewer)

        layout.addWidget(self.stageCamWidget)

        self.confirmWidget = QFrame()
        self.confirmWidget.setLayout(QVBoxLayout())
        self.confirmWidget.layout().addWidget(self.alignmentDisplay)
        self.confirmWidget.layout().addWidget(self.ignoreRotCheck)
        self.confirmWidget.layout().addWidget(self.ignoreScaleCheck)
        self.confirmWidget.layout().addWidget(self.flipCheck)

        layout.addWidget(self.confirmWidget)

        buttonsLayout = QHBoxLayout()
        buttonsLayout.setAlignment(Qt.AlignRight)
        buttonsLayout.addWidget(self.cancelButton)
        buttonsLayout.addWidget(self.markButton)
        buttonsLayout.addWidget(self.startButton)
        layout.addLayout(buttonsLayout)

        self.UpdateStateView()
        self.setLayout(layout)

    def Begin(self):
        self.state = PunchJobAlignmentWidget.STATE_MARK_DOT
        self.stageSystem.SetPosition(x=self.calibrationSettings.cameraDotPosition.x(),
                                     y=self.calibrationSettings.cameraDotPosition.x(),
                                     z=self.stageSystem.zSettings.minimum)
        self.cadViewer.highlightCircle = None
        self.UpdateStateView()

    def UpdateStateView(self):
        self.cadViewer.setVisible(self.state != PunchJobAlignmentWidget.STATE_MARK_DOT and
                                  self.state != PunchJobAlignmentWidget.STATE_CONFIRM_DESIGN)
        self.cadViewer.setEnabled(self.state == PunchJobAlignmentWidget.STATE_SELECT_FIRST or
                                  self.state == PunchJobAlignmentWidget.STATE_SELECT_SECOND)
        self.stageViewer.setVisible(self.state == PunchJobAlignmentWidget.STATE_MARK_DOT or
                                    self.state == PunchJobAlignmentWidget.STATE_MARK_FIRST or
                                    self.state == PunchJobAlignmentWidget.STATE_MARK_SECOND or
                                    self.state == PunchJobAlignmentWidget.STATE_CONFIRM_DESIGN)
        self.stageViewer.setEnabled(self.state != PunchJobAlignmentWidget.STATE_CONFIRM_DESIGN)
        self.cameraViewer.setVisible(self.state == PunchJobAlignmentWidget.STATE_MARK_DOT or
                                     self.state == PunchJobAlignmentWidget.STATE_MARK_FIRST or
                                     self.state == PunchJobAlignmentWidget.STATE_MARK_SECOND)
        self.startButton.setVisible(self.state == PunchJobAlignmentWidget.STATE_CONFIRM_DESIGN)
        self.confirmWidget.setVisible(self.state == PunchJobAlignmentWidget.STATE_CONFIRM_DESIGN)
        self.markButton.setVisible(self.state == PunchJobAlignmentWidget.STATE_MARK_DOT or
                                   self.state == PunchJobAlignmentWidget.STATE_MARK_FIRST or
                                   self.state == PunchJobAlignmentWidget.STATE_MARK_SECOND)

        self.designItem.setVisible(self.state == PunchJobAlignmentWidget.STATE_CONFIRM_DESIGN)

        self.instructionsText.setText(PunchJobAlignmentWidget.instructionText[self.state])

        self.cadViewer.RefreshDesign()

        self.stageCamWidget.setVisible(self.state == PunchJobAlignmentWidget.STATE_MARK_DOT or
                                       self.state == PunchJobAlignmentWidget.STATE_MARK_FIRST or
                                       self.state == PunchJobAlignmentWidget.STATE_MARK_SECOND or
                                       self.state == PunchJobAlignmentWidget.STATE_CONFIRM_DESIGN)

        self.UpdateAlignmentText()

    def HandleCircleClick(self, circle: Circle):
        if self.state == PunchJobAlignmentWidget.STATE_SELECT_FIRST:
            self.design.circleA = circle
            self.cadViewer.highlightCircle = circle
            self.state = PunchJobAlignmentWidget.STATE_MARK_FIRST
        elif self.state == PunchJobAlignmentWidget.STATE_SELECT_SECOND:
            self.design.circleB = circle
            self.cadViewer.highlightCircle = circle
            self.state = PunchJobAlignmentWidget.STATE_MARK_SECOND

        self.UpdateStateView()

    def MarkPosition(self):
        pos = self.stageSystem.GetPosition()
        pos = QPointF(pos[0], pos[1])
        if self.state == PunchJobAlignmentWidget.STATE_MARK_DOT:
            self.calibrationSettings.cameraDotPosition = pos
            self.cadViewer.highlightCircle = None
            self.state = PunchJobAlignmentWidget.STATE_SELECT_FIRST
        elif self.state == PunchJobAlignmentWidget.STATE_MARK_FIRST:
            self.design.globalA = pos
            self.cadViewer.highlightCircle = None
            self.state = PunchJobAlignmentWidget.STATE_SELECT_SECOND
        elif self.state == PunchJobAlignmentWidget.STATE_MARK_SECOND:
            self.design.globalB = pos
            self.cadViewer.highlightCircle = None
            self.state = PunchJobAlignmentWidget.STATE_CONFIRM_DESIGN

        self.designItem.CacheCircles()

        self.UpdateStateView()

    def UpdateAlignmentText(self):
        scale = self.design.CalculateScale()
        rotation = math.degrees(self.design.CalculateRotation())

        self.alignmentDisplay.setText("Rotation: " + str(rotation) + " degrees\nScale: " + str(scale))

    def Flip(self, checked: bool):
        self.design.flipY = bool(checked)

        self.designItem.CacheCircles()

        self.UpdateAlignmentText()

    def IgnoreScale(self, checked: bool):
        self.design.ignoreScale = bool(checked)

        self.designItem.CacheCircles()

        self.UpdateAlignmentText()

    def IgnoreRotation(self, checked: bool):
        self.design.ignoreRotation = bool(checked)

        self.designItem.CacheCircles()

        self.UpdateAlignmentText()