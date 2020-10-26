import typing


class PunchTip:
    def __init__(self, name="Unnamed Punch Tip", depth=0, diameter=1):
        self.name = name
        self.punchDepth = depth
        self.diameter = diameter


class PunchTips:
    def __init__(self):
        self.tips: typing.List[PunchTip] = []
