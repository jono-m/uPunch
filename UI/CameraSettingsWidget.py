from PySide2.QtWidgets import *
from UI.CameraViewerWidget import *
from Util import Event


class CameraSettingsWidget(QFrame):
    def __init__(self, alignmentCamera: AlignmentCamera):
        super().__init__()

        self.alignmentCamera = alignmentCamera
        self.alignmentCamera.OnDisconnect.Register(self.RescanCameras)

        self.cameraListLabel = QLabel("Detected Cameras: ")
        self.cameraList = QListWidget()
        self.cameraList.currentRowChanged.connect(self.SelectCamera)
        self.rescanButton = QPushButton("Rescan")
        self.rescanButton.clicked.connect(self.RescanCameras)

        self.cameraWidthLabel = QLabel("Camera Width (mm): ")
        self.cameraWidthField = QDoubleSpinBox()
        self.cameraWidthField.setMinimum(0.01)
        self.cameraWidthField.setMaximum(1000)
        self.cameraWidthField.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        self.cameraWidthField.valueChanged.connect(self.UpdateCameraWidth)
        self.micronsPerPixelLabel = QLabel()

        optionsLayout = QVBoxLayout()
        optionsLayout.addWidget(self.cameraListLabel)
        optionsLayout.addWidget(self.cameraList)
        optionsLayout.addWidget(self.rescanButton)
        widthLayout = QHBoxLayout()
        widthLayout.addWidget(self.cameraWidthLabel)
        widthLayout.addWidget(self.cameraWidthField)
        optionsLayout.addLayout(widthLayout)
        optionsLayout.addWidget(self.micronsPerPixelLabel)

        self.cameraPreview = CameraViewerWidget(alignmentCamera, 30)
        self.cameraPreviewLabel = QLabel()
        self.cameraPreviewLabel.setAlignment(Qt.AlignCenter)

        cameraPreviewLayout = QVBoxLayout()
        cameraPreviewLayout.addWidget(self.cameraPreview, stretch=1)
        cameraPreviewLayout.addWidget(self.cameraPreviewLabel, stretch=0)

        mainLayout = QHBoxLayout()
        mainLayout.addLayout(optionsLayout)
        mainLayout.addLayout(cameraPreviewLayout)
        self.setLayout(mainLayout)

        self.RescanCameras()

    def UpdateFields(self):
        self.micronsPerPixelLabel.setText("(" + str(self.alignmentCamera.MicronsPerPixel()) + " μm/pixel)")
        self.cameraWidthField.setValue(self.alignmentCamera.width)
        self.cameraPreviewLabel.setText(self.alignmentCamera.GetCameraName() + \
                                        "\nPreview")

    def UpdateCameraWidth(self, value):
        self.alignmentCamera.width = value
        self.UpdateFields()

    def SelectCamera(self, index):
        self.alignmentCamera.ActivateCamera(self.alignmentCamera.cameraList[index])
        self.UpdateFields()

    def RescanCameras(self):
        self.cameraList.blockSignals(True)
        self.cameraList.clear()
        self.alignmentCamera.UpdateCameraList()
        selectedIndex = -1
        for camera in self.alignmentCamera.cameraList:
            self.cameraList.addItem(camera.description())
            if camera == self.alignmentCamera.activeCameraInfo:
                selectedIndex = self.cameraList.count() - 1
        if selectedIndex >= 0:
            self.cameraList.setCurrentRow(selectedIndex)
        self.cameraList.blockSignals(False)
        self.UpdateFields()