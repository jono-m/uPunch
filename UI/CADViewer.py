from PySide2.QtWidgets import *
from PySide2.QtGui import *
from Data.Design import *
from Util import *


class CADViewer(QGraphicsView):
    def __init__(self, design: Design):
        super().__init__()

        self.setScene(QGraphicsScene(self))

        self.design = design

        self.setMinimumSize(QSize(500, 500))

    def RefreshDesign(self):
        self.scene().clear()

        for c in self.design.GetLocalCircles():
            brush = QBrush(QColor(255, 0, 0))
            self.scene().addEllipse(c.GetRect(), pen=Qt.NoPen, brush=brush)

        bRect = ScaleRectCenter(self.design.rect, 1.2)
        self.setSceneRect(bRect)
        self.fitInView(self.sceneRect())
