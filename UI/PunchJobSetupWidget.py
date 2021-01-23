from PySide2.QtWidgets import *
from UI.CADEditor import *
from UI.PunchJobDialog import *


class PunchJobSetupWidget(QFrame):
    def __init__(self, calibrationSettings: CalibrationSettings, alignmentCamera: AlignmentCamera,
                 stageSystem: StageSystem):
        super().__init__()

        self.calibrationSettings = calibrationSettings
        self.alignmentCamera = alignmentCamera
        self.stageSystem = stageSystem

        self.OnNext = Event()

        self.design = Design()

        self.fileLabel = QLabel("CAD File: ")
        self.fileField = QLineEdit()
        self.fileField.setEnabled(False)
        self.browseButton = QPushButton("Browse...")
        self.browseButton.clicked.connect(self.BrowseForDXF)

        self.cadViewer = CADEditor(self.design)
        self.cadViewer.OnCircleClicked.Register(self.HandleCircleClick)
        self.layerList = LayerList(self.design)
        self.layerList.OnChanged.Register(self.UpdateView)

        self.blockList = BlockList(self.design)
        self.blockList.OnChanged.Register(self.UpdateView)

        self.instructionsText = QLabel()

        self.circleCount = QLabel("")

        self.alignmentButton = QPushButton("Start Alignment")
        self.alignmentButton.clicked.connect(lambda: self.OnNext.Invoke())

        layout = QVBoxLayout()
        layout.addWidget(self.instructionsText)
        fileLayout = QHBoxLayout()
        fileLayout.addWidget(self.fileLabel)
        fileLayout.addWidget(self.fileField)
        fileLayout.addWidget(self.browseButton)

        sideLayout = QVBoxLayout()
        sideLayout.setAlignment(Qt.AlignTop)
        sideLayout.addWidget(self.layerList, stretch=1)
        sideLayout.addWidget(self.blockList, stretch=1)
        sideLayout.addWidget(self.circleCount)
        sideLayout.addWidget(self.alignmentButton)

        cadLayout = QHBoxLayout()
        cadLayout.addWidget(self.cadViewer, stretch=1)
        cadLayout.addLayout(sideLayout, stretch=0)

        layout.addLayout(fileLayout)
        layout.addLayout(cadLayout)

        self.setLayout(layout)

        self.UpdateView()

    def HandleCircleClick(self, c: Circle):
        c.specificallyIgnored = not c.specificallyIgnored

        self.UpdateView()

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
                else:
                    self.UpdateView()
                    return True
        return False

    def UpdateView(self):
        self.fileField.setText(self.design.filename)
        self.layerList.Repopulate()
        self.blockList.Repopulate()
        self.cadViewer.RefreshDesign()
        circleCount = len([c for c in self.design.GetLocalCircles() if not c.specificallyIgnored])
        self.circleCount.setText("<b>" + str(circleCount) + "</b> punch spots.")

        if self.design.filename == "":
            self.instructionsText.setText("Welcome to μPunch. Open a CAD design to get started.")
            self.alignmentButton.setEnabled(False)
        else:
            self.instructionsText.setText("Select layers and design blocks to be punched. "
                                          "Click on individual spots to enable/disable. ")
            self.alignmentButton.setEnabled(circleCount >= 2)


class LayerList(QFrame):
    def __init__(self, design: Design):
        super().__init__()

        self.design = design

        self.OnChanged = Event()

        self.scrollArea = QScrollArea()

        self.contents = QFrame()

        mainLayout = QVBoxLayout()
        mainLayout.setAlignment(Qt.AlignTop)
        mainLayout.addWidget(QLabel("<b>Active Layers:</b>"))

        self.layerLayout = QVBoxLayout()
        self.layerLayout.setAlignment(Qt.AlignTop)
        mainLayout.addLayout(self.layerLayout)
        self.contents.setLayout(mainLayout)

        self.scrollArea.setWidget(self.contents)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.scrollArea)
        self.setLayout(layout)

    def Repopulate(self):
        clearLayout(self.layerLayout)

        for layer in self.design.GetLayers():
            toggle = QCheckBox(layer)
            toggle.setChecked(self.design.GetLayers()[layer])
            toggle.stateChanged.connect(lambda state, l=layer: self.UpdateLayerState(state, l))
            self.layerLayout.addWidget(toggle)

    def UpdateLayerState(self, state, layer):
        self.design.SetLayerEnabled(layer, bool(state))
        self.Repopulate()
        self.OnChanged.Invoke()


class BlockList(QFrame):
    def __init__(self, design: Design):
        super().__init__()

        self.design = design

        self.OnChanged = Event()

        self.scrollArea = QScrollArea()

        self.contents = QFrame()

        mainLayout = QVBoxLayout()
        mainLayout.setAlignment(Qt.AlignTop)
        mainLayout.addWidget(QLabel("<b>Active Blocks:</b>"))

        self.blockLayout = QVBoxLayout()
        self.blockLayout.setAlignment(Qt.AlignTop)
        mainLayout.addLayout(self.blockLayout)
        self.contents.setLayout(mainLayout)

        self.scrollArea.setWidget(self.contents)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.scrollArea)
        self.setLayout(layout)

    def Repopulate(self):
        clearLayout(self.blockLayout)

        for block in self.design.GetBlocks():
            toggle = QCheckBox(block)
            toggle.setChecked(self.design.GetBlocks()[block])
            toggle.stateChanged.connect(lambda state, l=block: self.UpdateBlockState(state, l))
            self.blockLayout.addWidget(toggle)

        self.contents.adjustSize()
        self.scrollArea.setMinimumWidth(self.contents.width() + self.scrollArea.verticalScrollBar().width())

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
