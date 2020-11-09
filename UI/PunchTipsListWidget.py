from Data.PunchTips import *
from Util import *


class PunchTipsListWidget(QListWidget):
    def __init__(self, punchTips: PunchTips):
        super().__init__()

        self.punchTips = punchTips

        self.selectedTip: typing.Optional[PunchTip] = None

        self.currentRowChanged.connect(self.HandleSelection)

        self.OnPunchSelected = Event()

        self.UpdateList()

    def HandleSelection(self, index):
        self.selectedTip = self.punchTips.tips[index]
        self.OnPunchSelected.Invoke(self.selectedTip)

    def UpdateList(self):
        lastIndex = self.currentRow()

        self.blockSignals(True)
        self.clear()

        selectedIndex = -1
        for punchTip in self.punchTips.tips:
            self.addItem(punchTip.name + " (d: " + str(punchTip.diameter) + "mm, h: " + str(punchTip.punchDepth) + "mm)")
            if punchTip == self.selectedTip:
                selectedIndex = self.count()-1

        if selectedIndex >= 0:
            self.setCurrentRow(selectedIndex)
        else:
            if self.count() > 0:
                self.setCurrentRow(max(0, lastIndex-1))
                self.HandleSelection(max(0, lastIndex-1))
            else:
                self.selectedTip = None

        self.blockSignals(False)