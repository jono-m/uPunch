from PySide2.QtWidgets import *
from UI.CADEditor import *
from UI.PunchJobDialog import *


class PunchJobSetupWidget(QFrame):
    def __init__(self, punchTips: PunchTips, calibrationSettings: CalibrationSettings, alignmentCamera: AlignmentCamera,
                 stageSystem: StageSystem):
        super().__init__()

        self.punchTips = punchTips
        self.calibrationSettings = calibrationSettings
        self.alignmentCamera = alignmentCamera
        self.stageSystem = stageSystem

        self.design = Design()

        self.fileLabel = QLabel("CAD File: ")
        self.fileField = QLineEdit()
        self.fileField.setEnabled(False)
        self.browseButton = QPushButton("Browse...")
        self.browseButton.clicked.connect(self.BrowseForDXF)

        self.cadViewer = CADEditor(self.design)
        self.cadViewer.OnCircleClicked.Register(self.HandleCircleClick)
        self.cadViewer.CanHoverFunc = self.CanHoverCircle
        self.layerList = LayerList(self.design)
        self.layerList.OnChanged.Register(self.UpdateView)

        self.circleCount = QLabel("")

        self.aLabel = QLabel("Calibration Point A: ")
        self.aCoordinates = QLabel("")
        self.aButton = QPushButton("Select")
        self.aButton.clicked.connect(self.DoSelectA)

        self.bLabel = QLabel("Calibration Point B: ")
        self.bCoordinates = QLabel("")
        self.bButton = QPushButton("Select")
        self.bButton.clicked.connect(self.DoSelectB)
        self.alignmentButton = QPushButton("Start Alignment")
        self.alignmentButton.setProperty("NextButton", True)
        self.alignmentButton.clicked.connect(self.OpenAlignmentWindow)

        layout = QVBoxLayout()
        fileLayout = QHBoxLayout()
        fileLayout.addWidget(self.fileLabel)
        fileLayout.addWidget(self.fileField)
        fileLayout.addWidget(self.browseButton)

        aLayout = QVBoxLayout()
        aLayout.addWidget(self.aLabel)
        aLayout.addWidget(self.aCoordinates)
        aLayout.addWidget(self.aButton)
        bLayout = QVBoxLayout()
        bLayout.addWidget(self.bLabel)
        bLayout.addWidget(self.bCoordinates)
        bLayout.addWidget(self.bButton)
        ABLayout = QVBoxLayout()
        ABLayout.setAlignment(Qt.AlignTop)
        ABLayout.addLayout(aLayout)
        ABLayout.addLayout(bLayout)

        sideLayout = QVBoxLayout()
        sideLayout.setAlignment(Qt.AlignTop)
        sideLayout.addWidget(self.layerList, stretch=1)
        sideLayout.addLayout(ABLayout, stretch=0)
        sideLayout.addWidget(self.circleCount)
        sideLayout.addWidget(self.alignmentButton)

        cadLayout = QHBoxLayout()
        cadLayout.addWidget(self.cadViewer)
        cadLayout.addLayout(sideLayout)

        layout.addLayout(fileLayout)
        layout.addLayout(cadLayout)

        self.isSettingA = False
        self.isSettingB = False

        self.setLayout(layout)

        self.UpdateView()

    def DoSelectA(self):
        self.isSettingA = not self.isSettingA
        self.UpdateView()

    def DoSelectB(self):
        self.isSettingB = not self.isSettingB
        self.UpdateView()

    def HandleCircleClick(self, c: Circle):
        if self.isSettingA:
            self.design.circleA = c
            if self.design.circleB == c:
                self.design.circleB = None
        elif self.isSettingB:
            self.design.circleB = c
            if self.design.circleA == c:
                self.design.circleA = None
        else:
            c.specificallyIgnored = not c.specificallyIgnored
            if c.specificallyIgnored:
                if self.design.circleA == c:
                    self.design.circleA = None
                if self.design.circleB == c:
                    self.design.circleB = None

        self.isSettingA = False
        self.isSettingB = False

        self.UpdateView()

    def OpenAlignmentWindow(self):
        dialog = PunchJobDialog(self, self.design, self.punchTips, self.calibrationSettings, self.alignmentCamera,
                                self.stageSystem)
        dialog.exec_()

    def UpdateAB(self):
        if self.design.circleA is not None:
            self.aCoordinates.setText(
                "X: " + str(round(self.design.circleA.center.x(), 2)) +
                "\nY: " + str(round(self.design.circleA.center.y(), 2)))
        else:
            self.aCoordinates.setText("<b>NONE SELECTED</b>")
        if self.design.circleB is not None:
            self.bCoordinates.setText(
                "X: " + str(round(self.design.circleB.center.x(), 2)) +
                "\nY: " + str(round(self.design.circleB.center.y(), 2)))
        else:
            self.bCoordinates.setText("<b>NONE SELECTED</b>")

        self.alignmentButton.setEnabled(self.design.circleA is not None and self.design.circleB is not None)

        if self.isSettingA:
            self.aButton.setText("Cancel")
            self.bButton.setEnabled(False)
        else:
            self.aButton.setText("Select")
            self.bButton.setEnabled(True)

        if self.isSettingB:
            self.bButton.setText("Cancel")
            self.aButton.setEnabled(False)
        else:
            self.bButton.setText("Select")
            self.aButton.setEnabled(True)

        if self.isSettingA or self.isSettingB:
            self.cadViewer.SetInfoText("Choose a circle to use for alignment.")
        else:
            self.cadViewer.SetInfoText(None)

    def CanHoverCircle(self, c: Circle):
        if self.isSettingA or self.isSettingB:
            return not c.specificallyIgnored
        else:
            return True

    def BrowseForDXF(self):
        dialog = BrowseForDXFDialog(self)
        if dialog.exec_():
            filename = dialog.selectedFiles()

            if filename is not None:
                ret = self.design.LoadFromDXFFile(filename[0])
                if ret is not None:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setText("DXF Load Error")
                    msg.setInformativeText(ret)
                    msg.setWindowTitle("DXF Load Error")
                    msg.exec_()

        self.UpdateView()

    def UpdateView(self):
        self.fileField.setText(self.design.filename)
        self.layerList.Repopulate()
        self.cadViewer.RefreshDesign()
        self.UpdateAB()
        self.circleCount.setText("<b>" + str(
            len([c for c in self.design.GetLocalCircles() if not c.specificallyIgnored])) + "</b> punch spots.")


class LayerList(QFrame):
    def __init__(self, design: Design):
        super().__init__()

        self.design = design

        self.OnChanged = Event()

        mainLayout = QVBoxLayout()
        mainLayout.setAlignment(Qt.AlignTop)
        mainLayout.addWidget(QLabel("<b>Active Layers:</b>"))

        self.layerLayout = QGridLayout()
        self.layerLayout.setAlignment(Qt.AlignTop)
        mainLayout.addLayout(self.layerLayout)
        self.setLayout(mainLayout)

    def Repopulate(self):
        clearLayout(self.layerLayout)

        i = 0
        for layer in self.design.GetLayers():
            self.layerLayout.addWidget(QLabel(layer), i, 0)
            toggle = QCheckBox()
            toggle.setChecked(self.design.GetLayers()[layer])
            toggle.stateChanged.connect(lambda state, l=layer: self.UpdateLayerState(state, l))
            self.layerLayout.addWidget(toggle, i, 1)
            i += 1

        for block in self.design.GetBlocks():
            self.layerLayout.addWidget(QLabel(block), i, 0)
            toggle = QCheckBox()
            toggle.setChecked(self.design.GetBlocks()[block])
            toggle.stateChanged.connect(lambda state, l=block: self.UpdateBlockState(state, l))
            self.layerLayout.addWidget(toggle, i, 1)
            i += 1

    def UpdateLayerState(self, state, layer):
        self.design.SetLayerEnabled(layer, bool(state))
        self.Repopulate()
        self.OnChanged.Invoke()

    def UpdateBlockState(self, state, block):
        self.design.SetBlockEnabled(block, bool(state))
        self.Repopulate()
        self.OnChanged.Invoke()

def clearLayout(layout):
    if layout is not None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                clearLayout(item.layout())


class BrowseForDXFDialog(QFileDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("Open a CAD dile")
        self.setFileMode(QFileDialog.ExistingFile)
        self.setAcceptMode(QFileDialog.AcceptOpen)
        self.setNameFilters(["CAD file (*.dxf)"])
