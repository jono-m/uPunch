from PySide2.QtWidgets import *
from UI.CameraViewerWidget import *
from Data.CalibrationSettings import *
from UI.StageViewerWidget import *
from UI.CADGraphicsItem import *
from Data.Design import *
from UI.CADEditor import *


# class JobFollowWidget(QFrame):
#     def __init__(self, pjd = None):
#         super().__init__()
#
#         self.pjd = pjd
#
#         self.stageViewer = StageViewerWidget(self.pjd.stageSystem, False)
#         self.stageViewer.setEnabled(False)
#
#         self.OnFinish = Event()
#         self.OnCancel = Event()
#
#         self.designItem = CADGraphicsItem(self.pjd.design)
#         self.stageViewer.xyViewer.scene().addItem(self.designItem)
#
#         self.stageViewer.setEnabled(False)
#
#         self.pjd.stageSystem.OnPunchFinish.Register(self.PunchFinished)
#         self.pjd.stageSystem.OnPanFinish.Register(self.PanFinished)
#
#         self.isInJob = False
#
#         self.currentCircleNumber = -1
#
#         self.circlesToPunch: typing.List[Circle] = []
#
#         self.cancelButton = QPushButton("Cancel")
#         self.cancelButton.clicked.connect(self.CancelJob)
#
#         layout = QVBoxLayout()
#         layout.addWidget(self.stageViewer)
#         buttons = QHBoxLayout()
#         buttons.addWidget(self.cancelButton)
#         layout.addLayout(buttons)
#
#         self.setLayout(layout)
#
#     def StartJob(self):
#         self.designItem.CacheCircles()
#         self.designItem.setPos(self.pjd.calibrationSettings.CameraToPunch(QPointF(0, 0)))
#         self.circlesToPunch = [c for c in self.pjd.design.GetAlignedCircles() if not c.specificallyIgnored]
#         for c in self.circlesToPunch:
#             c.center = self.pjd.calibrationSettings.CameraToPunch(c.center)
#         self.isInJob = True
#         self.currentCircleNumber = -1
#         self.PunchFinished()
#
#     def CancelJob(self):
#         self.isInJob = False
#         self.OnCancel.Invoke()
#
#     def PunchFinished(self):
#         if not self.isInJob:
#             return
#
#         self.currentCircleNumber += 1
#
#         if self.currentCircleNumber >= len(self.circlesToPunch):
#             self.isInJob = False
#             self.OnFinish.Invoke()
#             return
#
#         pos = self.circlesToPunch[self.currentCircleNumber].center
#         self.pjd.stageSystem.SetPosition(x=pos.x(), y=pos.y())
#
#     def PanFinished(self):
#         if not self.isInJob:
#             return
#         self.pjd.stageSystem.DoPunch()
