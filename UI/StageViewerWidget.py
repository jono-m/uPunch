from UI.StageXYViewerWidget import *
from UI.StageZViewerWidget import *
from UI.StageControllerWidget import *


class StageViewerWidget(QFrame):
    def __init__(self, stageSystem: StageSystem, controlZ=True, showZ=True):
        super().__init__()

        self.stageSystem = stageSystem

        if showZ:
            self.zViewer = StageZViewerWidget(stageSystem, controlZ)
            self.zViewer.OnClicked.Register(lambda p: self.stageSystem.SetPosition(z=p))

        self.xyViewer = StageXYViewerWidget(stageSystem)
        self.xyViewer.OnClicked.Register(lambda p: self.stageSystem.SetPosition(x=p.x(), y=p.y()))

        self.controller = StageControllerWidget(self.stageSystem, controlZ)

        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        layout.addWidget(QLabel("Stage X-Y Position"), 0, 0)
        if showZ:
            layout.addWidget(QLabel("Stage Depth"), 0, 1)
        layout.addWidget(QLabel("Control"), 0, 2)
        layout.addWidget(self.xyViewer, 1, 0)
        if showZ:
            layout.addWidget(self.zViewer, 1, 1)
        layout.addWidget(self.controller, 1, 2)
