from PySide2.QtWidgets import *
from Data.StageSystem import *
from UI.StageControllerWidget import *
from UI.StageViewerWidget import *


class StageSettingsWidget(QFrame):
    def __init__(self, stageSystem: StageSystem):
        super().__init__()

        self.stageSystem = stageSystem

        self.stageViewer = StageViewerWidget(stageSystem, True)

        self.deviceLabel = QLabel("Available COM Ports")
        self.deviceList = QListWidget()
        self.deviceList.currentRowChanged.connect(self.HandleSelection)

        self.xAxis = AxisSettingsBox(self.stageSystem.xSettings, "X-axis", self.stageSystem)
        self.yAxis = AxisSettingsBox(self.stageSystem.ySettings, "Y-axis", self.stageSystem)
        self.zAxis = AxisSettingsBox(self.stageSystem.zSettings, "Z-axis", self.stageSystem)
        self.xAxis.OnSettingsChanged.Register(self.stageSystem.FlushSettings)
        self.yAxis.OnSettingsChanged.Register(self.stageSystem.FlushSettings)
        self.zAxis.OnSettingsChanged.Register(self.stageSystem.FlushSettings)

        settingsLayout = QHBoxLayout()

        deviceLayout = QVBoxLayout()
        deviceLayout.addWidget(QLabel("Detected devices:"))
        deviceLayout.addWidget(self.deviceList)
        self.rescanButton = QPushButton("Rescan")
        self.rescanButton.clicked.connect(self.Rescan)
        self.homeButton = QPushButton("Re-Home")
        self.homeButton.clicked.connect(self.stageSystem.HomeAll)
        deviceLayout.addWidget(self.rescanButton)
        deviceLayout.addWidget(self.homeButton)

        settingsLayout.addLayout(deviceLayout)
        settingsLayout.addWidget(self.xAxis)
        settingsLayout.addWidget(self.yAxis)
        settingsLayout.addWidget(self.zAxis)

        layout = QVBoxLayout()
        layout.addLayout(settingsLayout, stretch=0)
        layout.addWidget(self.stageViewer, stretch=1)
        self.setLayout(layout)

        self.devices = None

        self.Rescan()

    def HandleSelection(self, index):
        self.stageSystem.Connect(self.devices[index][0])

        self.xAxis.UpdateFields()
        self.yAxis.UpdateFields()
        self.zAxis.UpdateFields()

    def Rescan(self):
        self.devices = self.stageSystem.GetDeviceList()
        self.deviceList.blockSignals(True)

        lastIndex = self.deviceList.currentRow()

        self.deviceList.clear()

        sIndex = -1
        for (port, description) in self.devices:
            self.deviceList.addItem(description + " (" + port + ")")
            if port == self.stageSystem.portName:
                sIndex = self.deviceList.count() - 1

        self.deviceList.blockSignals(False)

        if sIndex >= 0:
            self.deviceList.setCurrentRow(sIndex)
        else:
            if self.deviceList.count() > 0:
                self.deviceList.setCurrentRow(max(0, lastIndex - 1))
            else:
                self.stageSystem.Disconnect()


class AxisSettingsBox(QFrame):
    def __init__(self, axis: AxisSettings, title: str, stageSystem: StageSystem):
        super().__init__()

        self.title = title

        self.stageSystem = stageSystem

        self.axis = axis

        self.OnSettingsChanged = Event()

        self.titleLabel = QLabel()
        self.titleLabel.setProperty('isSectionHeader', True)

        self.slowPanLabel = QLabel("Slow Pan (mm/sec): ")
        self.slowPanField = QDoubleSpinBox()
        self.slowPanField.valueChanged.connect(self.UpdateParameters)
        self.slowPanField.setMinimum(0)
        self.slowPanField.setMaximum(50)

        self.fastPanLabel = QLabel("Fast Pan (mm/sec): ")
        self.fastPanField = QDoubleSpinBox()
        self.fastPanField.setMinimum(0)
        self.fastPanField.setMaximum(50)
        self.fastPanField.valueChanged.connect(self.UpdateParameters)

        self.indexLabel = QLabel("Device Index: ")
        self.indexField = QSpinBox()
        self.indexField.setMinimum(0)
        self.indexField.setMaximum(2)
        self.indexField.valueChanged.connect(self.UpdateParameters)

        self.minimumLabel = QLabel("Minimum Position (mm): ")
        self.minimumField = QDoubleSpinBox()
        self.minimumField.setMinimum(0)
        self.minimumField.setMaximum(350)
        self.minimumField.valueChanged.connect(self.UpdateParameters)
        self.minimumCurrentButton = QPushButton("Set To Current")
        self.minimumCurrentButton.clicked.connect(
            lambda: self.minimumField.setValue(self.stageSystem.GetPosition(self.axis)))

        self.maximumLabel = QLabel("Maximum Position (mm): ")
        self.maximumField = QDoubleSpinBox()
        self.maximumField.setMinimum(0)
        self.maximumField.setMaximum(350)
        self.maximumField.valueChanged.connect(self.UpdateParameters)
        self.maximumCurrentButton = QPushButton("Set To Current")
        self.maximumCurrentButton.clicked.connect(
            lambda: self.maximumField.setValue(self.stageSystem.GetPosition(self.axis)))

        self.maxSpeedLabel = QLabel("Max Speed (mm/sec): ")
        self.maxSpeedField = QDoubleSpinBox()
        self.maxSpeedField.setMinimum(0)
        self.maxSpeedField.setMaximum(50)
        self.maxSpeedField.valueChanged.connect(self.UpdateParameters)

        self.flipField = QCheckBox()
        self.flipField.setText("Flip Pan Orientation")
        self.flipField.stateChanged.connect(self.UpdateParameters)

        layout = QGridLayout()
        layout.setAlignment(Qt.AlignTop)

        layout.addWidget(self.titleLabel, 0, 0, 1, 3)

        layout.addWidget(self.indexLabel, 1, 0)
        layout.addWidget(self.indexField, 1, 1, 1, 2)

        layout.addWidget(self.minimumLabel, 2, 0)
        layout.addWidget(self.minimumField, 2, 1)
        layout.addWidget(self.minimumCurrentButton, 2, 2)

        layout.addWidget(self.maximumLabel, 3, 0)
        layout.addWidget(self.maximumField, 3, 1)
        layout.addWidget(self.maximumCurrentButton, 3, 2)

        layout.addWidget(self.maxSpeedLabel, 4, 0)
        layout.addWidget(self.maxSpeedField, 4, 1, 1, 2)

        layout.addWidget(self.slowPanLabel, 5, 0)
        layout.addWidget(self.slowPanField, 5, 1, 1, 2)

        layout.addWidget(self.fastPanLabel, 6, 0)
        layout.addWidget(self.fastPanField, 6, 1, 1, 2)

        layout.addWidget(self.flipField, 7, 0, 1, 3)

        self.setLayout(layout)
        self.UpdateFields()

    def UpdateFields(self):
        for x in self.children():
            x.blockSignals(True)

        self.titleLabel.setText("<b>" + self.title + "\n(" + self.stageSystem.GetAxisName(self.axis) + ")</b>")

        self.slowPanField.setValue(self.axis.panSlowSpeed)
        self.fastPanField.setValue(self.axis.panFastSpeed)
        self.indexField.setValue(self.axis.deviceIndex)
        self.minimumField.setValue(self.axis.minimum)
        self.maximumField.setValue(self.axis.maximum)
        self.maxSpeedField.setValue(self.axis.maxSpeed)
        self.flipField.setChecked(self.axis.flipOrientation)

        for x in self.children():
            x.blockSignals(False)

    def UpdateParameters(self):
        self.axis.panSlowSpeed = self.slowPanField.value()
        self.axis.panFastSpeed = self.fastPanField.value()
        self.axis.deviceIndex = self.indexField.value()
        self.axis.minimum = self.minimumField.value()
        self.axis.maximum = self.maximumField.value()
        self.axis.maxSpeed = self.maxSpeedField.value()
        self.axis.flipOrientation = self.flipField.isChecked()
        self.OnSettingsChanged.Invoke(self.axis)
        self.UpdateFields()
