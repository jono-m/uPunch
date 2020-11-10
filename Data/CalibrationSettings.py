from PySide2.QtCore import *
import dill
import os


class CalibrationSettings:
    def __init__(self):
        self.punchOffset = QPointF(0, 0)

        self.LoadSettings()

    def LoadSettings(self):
        if os.path.exists("calibrationSettings.pkl"):
            file = open("calibrationSettings.pkl", "rb")
            self.punchOffset = dill.load(file)
            file.close()

    def SaveSettings(self):
        file = open("calibrationSettings.pkl", "wb")
        dill.dump(self.punchOffset, file)
        file.close()
