from PySide2.QtWidgets import *
from PySide2.QtCore import *
from Data.PunchTips import *
from Data.StageSystem import *
from UI.PunchTipsListWidget import *
from UI.StageViewerWidget import *


class PunchTipsSettingsWidget(QFrame):
    def __init__(self, punchTips: PunchTips, stageSystem: StageSystem):
        super().__init__()

        self.punchTips = punchTips

        self.stageSystem = stageSystem

        self.selectedTip: typing.Optional[PunchTip] = None

        self.listWidget = PunchTipsListWidget(punchTips)
        self.listWidget.OnPunchSelected.Register(self.UpdateFields)
        self.listLabel = QLabel("Available punch tips:")

        self.addButton = QToolButton()
        self.addButton.setText("+")
        self.addButton.clicked.connect(self.AddNewTip)
        self.removeButton = QToolButton()
        self.removeButton.setText("-")
        self.removeButton.clicked.connect(self.RemoveCurrentTip)

        self.nameLabel = QLabel("Name: ")
        self.nameField = QLineEdit()
        self.nameField.textEdited.connect(self.OptionsChanged)

        self.diameterLabel = QLabel("Diameter (mm): ")
        self.diameterField = QDoubleSpinBox()
        self.diameterField.valueChanged.connect(self.OptionsChanged)

        self.depthLabel = QLabel("Punch Depth (mm): ")
        self.depthField = QDoubleSpinBox()
        self.depthField.valueChanged.connect(self.OptionsChanged)

        self.currentDepthButton = QPushButton("Set To Current")
        self.currentDepthButton.clicked.connect(lambda: self.depthField.setValue(self.stageSystem.GetPosition()[2]))

        self.saveButton = QPushButton("Save")
        self.saveButton.clicked.connect(self.SaveOptions)

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
        depthLayout.addWidget(self.currentDepthButton)

        optionsWidget = QFrame()
        optionsWidget.setObjectName("PunchTipOptions")
        optionsLayout = QVBoxLayout()
        optionsLayout.addLayout(nameLayout)
        optionsLayout.addLayout(diameterLayout)
        optionsLayout.addLayout(depthLayout)
        optionsLayout.addWidget(self.saveButton)
        optionsLayout.setAlignment(Qt.AlignTop)
        optionsWidget.setLayout(optionsLayout)

        mainLayout = QHBoxLayout()
        mainLayout.addLayout(listLayout)
        mainLayout.addWidget(optionsWidget)

        layout = QVBoxLayout()
        layout.addLayout(mainLayout, stretch=0)
        layout.addWidget(StageViewerWidget(self.stageSystem), stretch=1)

        self.setLayout(layout)

        self.UpdateFields()

    def SaveOptions(self):
        self.listWidget.selectedTip.name = self.nameField.text()
        self.listWidget.selectedTip.diameter = self.diameterField.value()
        self.listWidget.selectedTip.punchDepth = self.depthField.value()
        self.UpdateFields()

    def OptionsChanged(self):
        self.saveButton.setEnabled(True)

    def RemoveCurrentTip(self):
        if self.listWidget.selectedTip is not None:
            self.punchTips.tips.remove(self.listWidget.selectedTip)
        self.listWidget.UpdateList()

    def AddNewTip(self):
        newTip = PunchTip("New Punch Tip", 0, 0)
        self.punchTips.tips.append(newTip)
        self.listWidget.selectedTip = newTip
        self.listWidget.UpdateList()

    def UpdateFields(self):
        if self.listWidget.selectedTip is None:
            self.nameField.setText("")
            self.nameField.setEnabled(False)
            self.depthField.lineEdit().setVisible(False)
            self.depthField.setEnabled(False)
            self.diameterField.lineEdit().setVisible(False)
            self.diameterField.setEnabled(False)
            self.removeButton.setEnabled(False)
        else:
            self.nameField.setText(self.listWidget.selectedTip.name)
            self.nameField.setEnabled(True)
            self.depthField.lineEdit().setVisible(True)
            self.depthField.setValue(self.listWidget.selectedTip.punchDepth)
            self.depthField.setEnabled(True)
            self.diameterField.lineEdit().setVisible(True)
            self.diameterField.setValue(self.listWidget.selectedTip.diameter)
            self.diameterField.setEnabled(True)
            self.removeButton.setEnabled(True)

        self.saveButton.setEnabled(False)
        self.saveButton.clearFocus()