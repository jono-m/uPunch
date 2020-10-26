from PySide2.QtWidgets import *
from Data.StageSystem import *


class StageSettingsWidget(QFrame):
    def __init__(self, stageSystem: StageSystem):
        super().__init__()

        self.stageSystem = stageSystem
