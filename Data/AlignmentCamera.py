import cv2
from PySide2.QtCore import *
from PySide2.QtGui import *
import typing
from PySide2.QtMultimedia import *
from Util import Event
import os
import dill


class AlignmentCamera:
    def __init__(self):
        self.activeCamera: typing.Optional[cv2.VideoCapture] = None
        self.cameraList: typing.List[QCameraInfo] = []
        self.activeCameraInfo: typing.Optional[QCameraInfo] = None
        self.width = 1
        self.OnDisconnect = Event()
        self.OnCameraChange = Event()

        self.UpdateCameraList()

        self.LoadSettings()

    def LoadSettings(self):
        if os.path.exists("cameraSettings.pkl"):
            file = open("cameraSettings.pkl", "rb")
            data = dill.load(file)
            file.close()
            self.width = data[0]
            if 0 <= data[1] < len(self.cameraList):
                self.ActivateCamera(self.cameraList[data[1]])

    def SaveSettings(self):
        if self.activeCamera is not None:
            file = open("cameraSettings.pkl", "wb")
            dill.dump([self.width, self.cameraList.index(self.activeCameraInfo)], file)
            file.close()

    def GetCameraName(self):
        if self.activeCamera is None:
            return "No camera selected."
        else:
            return self.activeCameraInfo.description()

    def MillimetersPerPixel(self):
        if self.activeCamera is None:
            return 0
        return self.width / self.GetResolution().width()

    def ActivateCamera(self, camera: QCameraInfo):
        self.DisconnectCamera()
        if camera not in self.cameraList:
            return
        self.activeCameraInfo = camera
        self.activeCamera = cv2.VideoCapture(self.cameraList.index(self.activeCameraInfo), cv2.CAP_DSHOW)

    def GetResolution(self):
        if self.activeCamera is None:
            return None
        return QSize(self.activeCamera.get(cv2.cv2.CAP_PROP_FRAME_WIDTH),
                     self.activeCamera.get(cv2.cv2.CAP_PROP_FRAME_HEIGHT))

    def GetImage(self) -> typing.Optional[QImage]:
        if self.activeCamera is None:
            return None
        status, frame = self.activeCamera.read()
        if status:
            height, width, channel = frame.shape
            bytesPerLine = 3 * width
            return QImage(frame.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()
        else:
            self.activeCamera = None
            self.activeCameraInfo = None
            self.OnDisconnect.Invoke()

    def UpdateCameraList(self):
        self.cameraList = QCameraInfo.availableCameras()

    def DisconnectCamera(self):
        if self.activeCamera is not None:
            self.activeCamera.release()
            self.activeCameraInfo = None
            self.activeCamera = None
