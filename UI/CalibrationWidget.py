from PySide2.QtWidgets import *
from Data.AlignmentCamera import *
from Data.StageSystem import *
from Data.CalibrationSettings import *


class CalibrationWidget(QFrame):
    def __init__(self, calibrationSettings: CalibrationSettings, alignmentCamera: AlignmentCamera,
                 stageSystem: StageSystem):
        super().__init__()

        self.punchOffsetLabel = QLabel("Offset to punch (mm): ")