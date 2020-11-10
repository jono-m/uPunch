from PySide2.QtWidgets import *


class PunchJobSetupWidget(QFrame):
    def __init__(self):
        super().__init__()

        self.fileLabel = QLabel("CAD File: ")
        self.fileField = QLineEdit()
        self.fileField.setEnabled(False)
        self.browseButton = QPushButton("Browse...")
        self.browseButton.clicked.connect(self.BrowseForDWG)

        self.layerList = QFrame()

class LayerItem(QFrame):
    def __init__(self, layerName: str):