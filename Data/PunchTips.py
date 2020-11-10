import typing
import dill
import os


class PunchTip:
    def __init__(self, name="Unnamed Punch Tip", depth=0, diameter=1):
        self.name = name
        self.punchDepth = depth
        self.diameter = diameter


class PunchTips:
    def __init__(self):
        self.tips: typing.List[PunchTip] = []

        self.LoadSettings()

    def LoadSettings(self):
        if os.path.exists("tipSettings.pkl"):
            file = open("tipSettings.pkl", "rb")
            self.tips = dill.load(file)
            file.close()

    def SaveSettings(self):
        file = open("tipSettings.pkl", "wb")
        dill.dump(self.tips, file)
        file.close()
