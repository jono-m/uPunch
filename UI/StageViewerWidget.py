from UI.StageXYViewerWidget import *
from UI.StageZViewerWidget import *
from UI.StageControllerWidget import *


class StageViewerWidget(QFrame):
    def __init__(self, stageSystem: StageSystem, controlZ=True):
        super().__init__()

        self.stageSystem = stageSystem

        self.zViewer = StageZViewerWidget(stageSystem, controlZ)
        self.xyViewer = StageXYViewerWidget(stageSystem)
        self.xyViewer.OnClicked.Register(lambda p: self.stageSystem.SetPosition(x=p.x(), y=p.y()))

        self.zViewer.OnClicked.Register(lambda p: self.stageSystem.SetPosition(z=p))

        self.controller = StageControllerWidget(self.stageSystem, controlZ)

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(QLabel("Stage X-Y Position"), 0, 0)
        layout.addWidget(QLabel("Stage Depth"), 0, 1)
        layout.addWidget(QLabel("Control"), 0, 2)
        layout.addWidget(self.xyViewer, 1, 0)
        layout.addWidget(self.zViewer, 1, 1)
        layout.addWidget(self.controller, 1, 2)
