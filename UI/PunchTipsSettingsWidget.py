from PySide2.QtWidgets import *
from PySide2.QtCore import *
from Data.PunchTips import *


class PunchTipsSettingsWidget(QFrame):
    def __init__(self, punchTips: PunchTips):
        super().__init__()

        self.punchTips = punchTips

        self.selectedTip: typing.Optional[PunchTip] = None

        self.listWidget = QListWidget()
        self.listLabel = QLabel("Available punch tips:")
        self.listWidget.currentRowChanged.connect(self.HandleSelection)

        self.addButton = QPushButton("+")
        self.addButton.clicked.connect(self.AddNewTip)
        self.removeButton = QPushButton("-")
        self.removeButton.clicked.connect(self.RemoveCurrentTip)

        self.nameLabel = QLabel("Name: ")
        self.nameField = QLineEdit()

        self.diameterLabel = QLabel("Diameter (mm): ")
        self.diameterField = QDoubleSpinBox()

        self.depthLabel = QLabel("Punch Depth (mm): ")
        self.depthField = QDoubleSpinBox()

        buttonsLayout = QVBoxLayout()
        buttonsLayout.addWidget(self.addButton)
        buttonsLayout.addWidget(self.removeButton)
        buttonsLayout.setAlignment(Qt.AlignTop)

        listAndButtonsLayout = QHBoxLayout()
        listAndButtonsLayout.addWidget(self.listWidget)
        listAndButtonsLayout.addLayout(buttonsLayout)

        listLayout = QVBoxLayout()
        listLayout.addWidget(self.listLabel)
        listLayout.addLayout(listAndButtonsLayout)

        nameLayout = QHBoxLayout()
        nameLayout.addWidget(self.nameLabel)
        nameLayout.addWidget(self.nameField)

        diameterLayout = QHBoxLayout()
        diameterLayout.addWidget(self.diameterLabel)
        diameterLayout.addWidget(self.diameterField)

        depthLayout = QHBoxLayout()
        depthLayout.addWidget(self.depthLabel)
        depthLayout.addWidget(self.depthField)

        optionsWidget = QFrame()
        optionsWidget.setObjectName("PunchTipOptions")
        optionsLayout = QVBoxLayout()
        optionsLayout.addLayout(nameLayout)
        optionsLayout.addLayout(diameterLayout)
        optionsLayout.addLayout(depthLayout)
        optionsLayout.setAlignment(Qt.AlignTop)
        optionsWidget.setLayout(optionsLayout)

        mainLayout = QHBoxLayout()
        mainLayout.addLayout(listLayout)
        mainLayout.addWidget(optionsWidget)

        self.setLayout(mainLayout)

        self.UpdateList()

    def HandleSelection(self, index):
        self.selectedTip = self.punchTips.tips[index]
        self.UpdateFields()

    def RemoveCurrentTip(self):
        if self.selectedTip is not None:
            self.punchTips.tips.remove(self.selectedTip)
        self.UpdateList()

    def AddNewTip(self):
        newTip = PunchTip("New Punch Tip", 0, 0)
        self.punchTips.tips.append(newTip)
        self.selectedTip = newTip
        self.UpdateList()

    def UpdateList(self):
        lastIndex = self.listWidget.currentRow()

        self.listWidget.blockSignals(True)
        self.listWidget.clear()

        selectedIndex = -1
        for punchTip in self.punchTips.tips:
            self.listWidget.addItem(punchTip.name)
            if punchTip == self.selectedTip:
                selectedIndex = self.listWidget.count()-1

        if selectedIndex >= 0:
            self.listWidget.setCurrentRow(selectedIndex)
        else:
            if self.listWidget.count() > 0:
                self.listWidget.setCurrentRow(max(0, lastIndex-1))
                self.HandleSelection(max(0, lastIndex-1))
            else:
                self.selectedTip = None

        self.listWidget.blockSignals(False)

        self.UpdateFields()

    def UpdateFields(self):
        if self.selectedTip is None:
            self.nameField.setText("")
            self.nameField.setEnabled(False)
            self.depthField.lineEdit().setVisible(False)
            self.depthField.setEnabled(False)
            self.diameterField.lineEdit().setVisible(False)
            self.diameterField.setEnabled(False)
            self.removeButton.setEnabled(False)
        else:
            self.nameField.setText(self.selectedTip.name)
            self.nameField.setEnabled(True)
            self.depthField.lineEdit().setVisible(True)
            self.depthField.setValue(self.selectedTip.punchDepth)
            self.depthField.setEnabled(True)
            self.diameterField.lineEdit().setVisible(True)
            self.diameterField.setValue(self.selectedTip.diameter)
            self.diameterField.setEnabled(True)
            self.removeButton.setEnabled(True)
