from PySide2.QtCore import *
import dill
import os


class CalibrationSettings:
    def __init__(self):
        self.punchDotPosition = QPointF(100, 100)
        self.cameraDotPosition = QPointF(50, 100)

        self.LoadSettings()

    def CameraToPunch(self, cameraPoint: QPointF):
        return cameraPoint + (self.punchDotPosition - self.cameraDotPosition)

    def LoadSettings(self):
        if os.path.exists("calibrationSettings.pkl"):
            file = open("calibrationSettings.pkl", "rb")
            (self.punchDotPosition, self.cameraDotPosition) = dill.load(file)
            file.close()

    def SaveSettings(self):
        file = open("calibrationSettings.pkl", "wb")
        dill.dump((self.punchDotPosition, self.cameraDotPosition), file)
        file.close()
