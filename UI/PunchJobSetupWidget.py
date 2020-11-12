from PySide2.QtWidgets import *
from UI.CADViewer import *


class PunchJobSetupWidget(QFrame):
    def __init__(self):
        super().__init__()

        self.design = Design()

        self.fileLabel = QLabel("CAD File: ")
        self.fileField = QLineEdit()
        self.fileField.setEnabled(False)
        self.browseButton = QPushButton("Browse...")
        self.browseButton.clicked.connect(self.BrowseForDXF)

        self.cadViewer = CADViewer(self.design)
        self.layerList = LayerList(self.design)
        self.layerList.OnChanged.Register(self.cadViewer.RefreshDesign)

        layout = QVBoxLayout()
        fileLayout = QHBoxLayout()
        fileLayout.addWidget(self.fileLabel)
        fileLayout.addWidget(self.fileField)
        fileLayout.addWidget(self.browseButton)

        cadLayout = QHBoxLayout()
        cadLayout.addWidget(self.cadViewer)
        cadLayout.addWidget(self.layerList)

        layout.addLayout(fileLayout)
        layout.addLayout(cadLayout)

        self.setLayout(layout)

    def BrowseForDXF(self):
        dialog = BrowseForDXFDialog(self)
        self.fileField.setText("")
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
                    self.fileField.setText(filename[0])

        self.layerList.Repopulate()
        self.cadViewer.RefreshDesign()


class LayerList(QFrame):
    def __init__(self, design: Design):
        super().__init__()

        self.design = design

        self.OnChanged = Event()

        mainLayout = QVBoxLayout()
        mainLayout.setAlignment(Qt.AlignTop)
        mainLayout.addWidget(QLabel("Active Layers:"))

        self.layerLayout = QGridLayout()
        self.layerLayout.setAlignment(Qt.AlignTop)
        mainLayout.addLayout(self.layerLayout)
        self.setLayout(mainLayout)

    def Repopulate(self):
        clearLayout(self.layerLayout)

        i = 0
        for layer in self.design.layers:
            self.layerLayout.addWidget(QLabel(layer), i, 0)
            toggle = QCheckBox()
            toggle.setChecked(self.design.layers[layer])
            toggle.stateChanged.connect(lambda state, l=layer: self.UpdateState(state, l))
            self.layerLayout.addWidget(toggle, i, 1)
            i += 1

    def UpdateState(self, state, layer):
        self.design.layers[layer] = bool(state)
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
