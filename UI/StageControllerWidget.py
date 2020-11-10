from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
from Data.StageSystem import *


class StageControllerWidget(QFrame):
    def __init__(self, stageSystem: StageSystem, includeZ):
        super().__init__()

        self.stageSystem = stageSystem

        self.upSlow = PanArrow(False, False, False)
        self.upSlow.pressed.connect(lambda: self.stageSystem.PanAxis(self.stageSystem.ySettings, True, -1))
        self.upSlow.released.connect(lambda: self.stageSystem.StopPan())

        self.upFast = PanArrow(True, False, False)
        self.upFast.pressed.connect(lambda: self.stageSystem.PanAxis(self.stageSystem.ySettings, False, -1))
        self.upFast.released.connect(lambda: self.stageSystem.StopPan())

        self.downSlow = PanArrow(False, True, False)
        self.downSlow.pressed.connect(lambda: self.stageSystem.PanAxis(self.stageSystem.ySettings, True, 1))
        self.downSlow.released.connect(lambda: self.stageSystem.StopPan())

        self.downFast = PanArrow(True, True, False)
        self.downFast.pressed.connect(lambda: self.stageSystem.PanAxis(self.stageSystem.ySettings, False, 1))
        self.downFast.released.connect(lambda: self.stageSystem.StopPan())

        self.rightSlow = PanArrow(False, True, True)
        self.rightSlow.pressed.connect(lambda: self.stageSystem.PanAxis(self.stageSystem.xSettings, True, 1))
        self.rightSlow.released.connect(lambda: self.stageSystem.StopPan())

        self.rightFast = PanArrow(True, True, True)
        self.rightFast.pressed.connect(lambda: self.stageSystem.PanAxis(self.stageSystem.xSettings, False, 1))
        self.rightFast.released.connect(lambda: self.stageSystem.StopPan())

        self.leftSlow = PanArrow(False, False, True)
        self.leftSlow.pressed.connect(lambda: self.stageSystem.PanAxis(self.stageSystem.xSettings, True, -1))
        self.leftSlow.released.connect(lambda: self.stageSystem.StopPan())

        self.leftFast = PanArrow(True, False, True)
        self.leftFast.pressed.connect(lambda: self.stageSystem.PanAxis(self.stageSystem.xSettings, False, -1))
        self.leftFast.released.connect(lambda: self.stageSystem.StopPan())

        center = QLabel("PAN")
        gridLayout = QGridLayout()
        gridLayout.setContentsMargins(0, 0, 0, 0)
        gridLayout.setSpacing(0)
        gridLayout.addWidget(self.upSlow, 1, 2)
        gridLayout.addWidget(self.upFast, 0, 2)
        gridLayout.addWidget(self.downSlow, 3, 2)
        gridLayout.addWidget(self.downFast, 4, 2)
        gridLayout.addWidget(self.rightSlow, 2, 3)
        gridLayout.addWidget(self.rightFast, 2, 4)
        gridLayout.addWidget(self.leftSlow, 2, 1)
        gridLayout.addWidget(self.leftFast, 2, 0)
        gridLayout.addWidget(center, 2, 2)

        if includeZ:
            self.inFast = PanArrow(True, True, False)
            self.inFast.pressed.connect(lambda: self.stageSystem.PanAxis(self.stageSystem.zSettings, False, 1))
            self.inFast.released.connect(lambda: self.stageSystem.StopPan())

            self.inSlow = PanArrow(False, True, False)
            self.inSlow.pressed.connect(lambda: self.stageSystem.PanAxis(self.stageSystem.zSettings, True, 1))
            self.inSlow.released.connect(lambda: self.stageSystem.StopPan())

            self.outFast = PanArrow(True, False, False)
            self.outFast.pressed.connect(lambda: self.stageSystem.PanAxis(self.stageSystem.zSettings, False, -1))
            self.outFast.released.connect(lambda: self.stageSystem.StopPan())

            self.outSlow = PanArrow(False, False, False)
            self.outSlow.pressed.connect(lambda: self.stageSystem.PanAxis(self.stageSystem.zSettings, True, -1))
            self.outSlow.released.connect(lambda: self.stageSystem.StopPan())

            gridLayout.addWidget(Spacer(), 0, 5, 5, 1)
            gridLayout.addWidget(self.outFast, 0, 6)
            gridLayout.addWidget(self.outSlow, 1, 6)
            gridLayout.addWidget(QLabel("DEPTH"), 2, 6)
            gridLayout.addWidget(self.inSlow, 3, 6)
            gridLayout.addWidget(self.inFast, 4, 6)

        layout = QVBoxLayout()
        layout.addStretch(1)
        layout.addLayout(gridLayout, stretch=0)
        layout.addStretch(1)
        self.setLayout(layout)


class Spacer(QFrame):
    pass


class PanArrow(QToolButton):
    def __init__(self, isDouble, flipVertical, rotate90):
        super().__init__()

        if isDouble:
            image = QImage("Assets/doubleMoveArrow.png")
        else:
            image = QImage("Assets/singleMoveArrow.png")

        rotated = QImage(image.size(), image.format())
        for x in range(image.width()):
            for y in range(image.height()):
                pixel = image.pixel(x, y)
                fX = x
                fY = y
                if flipVertical:
                    fY = image.height() - fY
                if rotate90:
                    t = fX
                    fX = fY
                    fY = t
                rotated.setPixel(fX, fY, pixel)

        self.setIcon(QIcon(QPixmap.fromImage(rotated)))
