from zaber_motion import Library
from zaber_motion.ascii import Connection
from zaber_motion.ascii.device import Axis
from zaber_motion import Units
import typing
from Util import *
from PySide2.QtWidgets import *
import serial.tools.list_ports
import dill
import os

Library.enable_device_db_store()


class AxisSettings:
    def __init__(self, deviceIndex):
        self.deviceIndex = deviceIndex
        self.flipOrientation = False
        self.panSlowSpeed = 10
        self.panFastSpeed = 20
        self.minimum = 0
        self.maximum = 300
        self.maxSpeed = 10

        self.absMinimum = 0
        self.absMaximum = 300

    def ClampAxis(self, val):
        return min(self.maximum, max(self.minimum, val))

    def ClampAbsAxis(self, val):
        return min(self.absMaximum, max(self.absMinimum, val))


class StageSystem:
    STATE_IDLE = 0
    STATE_PUNCH_LOWER = 1
    STATE_PUNCH_RAISE = 2
    STATE_PAN = 3

    def __init__(self, widgetHost: QWidget):
        self._axisList: typing.List[Axis] = []
        self._activeConnection: typing.Optional[Connection] = None
        self.portName = ""
        self.OnDisconnect = Event()

        self.xSettings = AxisSettings(0)
        self.ySettings = AxisSettings(1)
        self.zSettings = AxisSettings(2)

        self.OnPunchBegin = Event()
        self.OnPunchFinish = Event()
        self.OnPanFinish = Event()

        self.widgetHost = widgetHost

        self.LoadSettings()

        self._isStationary = True

        self._lastPosition = None

        self.state = StageSystem.STATE_IDLE

        self.punchTimer = QTimer(widgetHost)
        self.punchTimer.timeout.connect(self.PunchTick)
        self.punchTimer.start()

    def DoPunch(self, depth):
        print(depth)
        if self.state != StageSystem.STATE_IDLE:
            return
        self.OnPunchBegin.Invoke()
        self.state = StageSystem.STATE_PUNCH_LOWER
        self.SetPosition(z=depth)

    def RaisePunch(self):
        self.state = StageSystem.STATE_PUNCH_RAISE
        self.SetPosition(z=self.zSettings.minimum)

    def PunchTick(self):
        if not self.IsMoving():
            if self.state == StageSystem.STATE_PUNCH_RAISE:
                self.state = StageSystem.STATE_IDLE
                self.OnPunchFinish.Invoke()
            elif self.state == StageSystem.STATE_PUNCH_LOWER:
                self.RaisePunch()
            elif self.state == StageSystem.STATE_PAN:
                self.state = StageSystem.STATE_IDLE
                self.OnPanFinish.Invoke()

    def LoadSettings(self):
        if os.path.exists("stageSettings.pkl"):
            file = open("stageSettings.pkl", "rb")
            [self.xSettings,
             self.ySettings,
             self.zSettings,
             self.portName] = dill.load(file)
            file.close()

    def SaveSettings(self):
        file = open("stageSettings.pkl", "wb")
        dill.dump([self.xSettings, self.ySettings, self.zSettings, self.portName], file)
        file.close()

    def Connect(self, portName: str):
        self.Disconnect()

        if portName not in [p[0] for p in self.GetDeviceList()]:
            self.portName = ""
            return
        else:
            self.portName = portName

        self._activeConnection = Connection.open_serial_port(self.portName)
        self._activeConnection.disconnected.subscribe(lambda alert: self.OnDisconnect.Invoke())
        try:
            self._axisList = [device.get_axis(1) for device in self._activeConnection.detect_devices()]
        except:
            self._activeConnection = None
            self.portName = ""
            return

        devices = self._activeConnection.detect_devices()
        for d in devices:
            d.all_axes.unpark()

        self.FlushSettings(self.xSettings)
        self.FlushSettings(self.ySettings)
        self.FlushSettings(self.zSettings)

    def GetAxisName(self, axis: AxisSettings) -> str:
        if not self.IsConnected():
            return "[]"
        return self._axisList[axis.deviceIndex].device.name

    def IsConnected(self) -> bool:
        return self._activeConnection is not None

    def Disconnect(self):
        if self.IsConnected():
            devices = self._activeConnection.detect_devices()
            for d in devices:
                d.all_axes.park()

            self.portName = ""
            self._activeConnection.close()

    def HomeAll(self):
        for axis in self._axisList:
            axis.home(False)
        self._isStationary = False

    def IsHomed(self) -> bool:
        for axis in self._axisList:
            if axis.settings.get("limit.home.triggered") == 0:
                return False

        return True

    def FlushSettings(self, settings: AxisSettings):
        settings.absMinimum = self._axisList[settings.deviceIndex].settings.get("limit.min", Units.LENGTH_MILLIMETRES)
        settings.absMaximum = self._axisList[settings.deviceIndex].settings.get("limit.max", Units.LENGTH_MILLIMETRES)

        settings.minimum = settings.ClampAbsAxis(settings.minimum)
        settings.maximum = settings.ClampAbsAxis(settings.maximum)

        self._axisList[settings.deviceIndex].settings.set("maxspeed", settings.maxSpeed,
                                                          Units.VELOCITY_MILLIMETRES_PER_SECOND)

    def IsMoving(self) -> bool:
        if self._isStationary:
            return False

        for axis in self._axisList:
            if axis.is_busy():
                return True
        self._isStationary = True
        return False

    def ClampPoint(self, pos: QPointF):
        return QPointF(self.xSettings.ClampAxis(pos.x()), self.ySettings.ClampAxis(pos.y()))

    def GetPosition(self, axis: typing.Optional[AxisSettings] = None) -> \
            typing.Union[typing.Tuple[float, float, float], float]:
        if not self.IsConnected():
            return 0, 0, 0
        if self._isStationary and self._lastPosition is not None:
            if axis is None:
                return self._lastPosition
            else:
                if axis == self.xSettings:
                    return self._lastPosition[0]
                if axis == self.ySettings:
                    return self._lastPosition[1]
                if axis == self.zSettings:
                    return self._lastPosition[2]
        if axis is None:
            x = self._axisList[self.xSettings.deviceIndex].get_position(Units.LENGTH_MILLIMETRES)
            y = self._axisList[self.ySettings.deviceIndex].get_position(Units.LENGTH_MILLIMETRES)
            z = self._axisList[self.zSettings.deviceIndex].get_position(Units.LENGTH_MILLIMETRES)
            self._lastPosition = (x, y, z)
            return x, y, z
        else:
            return self._axisList[axis.deviceIndex].get_position(Units.LENGTH_MILLIMETRES)

    def MoveXY(self, offset: QPointF):
        currentPosition = self.GetPosition()
        xy = QPointF(currentPosition[0], currentPosition[1])
        final = xy + offset
        self.SetPosition(x=final.x(), y=final.y())

    def SetPosition(self, x=None, y=None, z=None):
        if self.IsMoving():
            return

        if x is not None:
            x = self.xSettings.ClampAxis(x)
            self._axisList[self.xSettings.deviceIndex].move_absolute(x, Units.LENGTH_MILLIMETRES, False)
            self.state = StageSystem.STATE_PAN
        if y is not None:
            y = self.ySettings.ClampAxis(y)
            self._axisList[self.ySettings.deviceIndex].move_absolute(y, Units.LENGTH_MILLIMETRES, False)
            self.state = StageSystem.STATE_PAN
        if z is not None:
            z = self.zSettings.ClampAxis(z)
            self._axisList[self.zSettings.deviceIndex].move_absolute(z, Units.LENGTH_MILLIMETRES, False)

        self._isStationary = False

    def GetPanVelocity(self, axisSettings: AxisSettings, shouldPanSlow, direction):
        if axisSettings.flipOrientation:
            direction = -direction

        if shouldPanSlow:
            return axisSettings.panSlowSpeed * direction
        else:
            return axisSettings.panFastSpeed * direction

    def PanAxis(self, axisSettings: AxisSettings, slowSpeed, direction):
        if self.IsMoving():
            return
        self._axisList[axisSettings.deviceIndex].move_velocity(self.GetPanVelocity(axisSettings, slowSpeed, direction),
                                                               Units.VELOCITY_MILLIMETRES_PER_SECOND)

        self._isStationary = False

    def StopPan(self):
        self._axisList[self.xSettings.deviceIndex].stop(False)
        self._axisList[self.ySettings.deviceIndex].stop(False)
        self._axisList[self.zSettings.deviceIndex].stop(False)

        self._isStationary = True

    def GetDeviceList(self) -> typing.List[typing.Tuple[str, str]]:
        return [(comport.device, comport.description) for comport in serial.tools.list_ports.comports()]
