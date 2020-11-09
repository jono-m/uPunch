from zaber_motion import Library
from zaber_motion.ascii import Connection
from zaber_motion.ascii.device import Axis
from zaber_motion import Units
import typing
from Util import *
from Data.Data3D import *
from PySide2.QtWidgets import *
import serial.tools.list_ports

Library.enable_device_db_store()


class AxisSettings:
    def __init__(self, deviceIndex):
        self.deviceIndex = deviceIndex
        self.flipOrientation = False
        self.panSlowSpeed = 10
        self.panFastSpeed = 20
        self.minimum = 0
        self.maximum = 300
        self.maxSpeed = 50

    def ClampAxis(self, val):
        return min(self.maximum, max(self.minimum, val))


class StageSystem:
    def __init__(self):
        self._axisList: typing.List[Axis] = []
        self._activeConnection: typing.Optional[Connection] = None
        self.portName = "NOT CONNECTED"
        self.OnDisconnect = Event()

        self.xSettings = AxisSettings(0)
        self.ySettings = AxisSettings(1)
        self.zSettings = AxisSettings(2)

    def Connect(self, portName: str):
        self.Disconnect()
        self.portName = portName
        self._activeConnection = Connection.open_serial_port(self.portName)
        self._activeConnection.disconnected.subscribe(lambda alert: self.OnDisconnect.Invoke())
        self._axisList = [device.get_axis(1) for device in self._activeConnection.detect_devices()]

    def GetDeviceName(self) -> str:
        if not self.IsConnected():
            return "[]"
        xName = "[X: " + self._axisList[self.xSettings.deviceIndex].device.name + "]\n"
        yName = "[Y: " + self._axisList[self.ySettings.deviceIndex].device.name + "]\n"
        zName = "[Z: " + self._axisList[self.zSettings.deviceIndex].device.name + "]\n"
        return xName + yName + zName

    def IsConnected(self) -> bool:
        return self._activeConnection is not None

    def Disconnect(self):
        self._activeConnection.close()

    def HomeAll(self):
        for axis in self._axisList:
            axis.home(False)

    def IsHomed(self) -> bool:
        for axis in self._axisList:
            if axis.settings.get("limit.home.triggered") == 0:
                return False

        return True

    def FlushSettings(self, settings: AxisSettings):
        self._axisList[settings.deviceIndex].settings.set("maxspeed", settings.maxSpeed,
                                                          Units.VELOCITY_MILLIMETRES_PER_SECOND)
        self._axisList[settings.deviceIndex].settings.set("limit.min", settings.minimum, Units.LENGTH_MILLIMETRES)
        self._axisList[settings.deviceIndex].settings.set("limit.max", settings.maximum, Units.LENGTH_MILLIMETRES)

    def IsMoving(self) -> bool:
        for axis in self._axisList:
            if axis.is_busy():
                return True
        return False

    def ClampPoint(self, pos: QPointF):
        return QPointF(self.xSettings.ClampAxis(pos.x()), self.ySettings.ClampAxis(pos.y()))

    def GetPosition(self, axis: typing.Optional[AxisSettings] = None) -> \
            typing.Union[typing.Tuple[float, float, float], float]:
        if axis is None:
            x = self._axisList[self.xSettings.deviceIndex].get_position(Units.LENGTH_MILLIMETRES)
            y = self._axisList[self.ySettings.deviceIndex].get_position(Units.LENGTH_MILLIMETRES)
            z = self._axisList[self.zSettings.deviceIndex].get_position(Units.LENGTH_MILLIMETRES)
            return x, y, z
        else:
            return self._axisList[axis.deviceIndex].get_position(Units.LENGTH_MILLIMETRES)

    def SetPosition(self, x=None, y=None, z=None):
        print(str(x) + " - " + str(y) + " - " + str(z))
        if self.IsMoving():
            return

        if x is not None:
            self._axisList[self.xSettings.deviceIndex].move_absolute(x, Units.LENGTH_MILLIMETRES, False)
        if y is not None:
            self._axisList[self.ySettings.deviceIndex].move_absolute(y, Units.LENGTH_MILLIMETRES, False)
        if z is not None:
            self._axisList[self.zSettings.deviceIndex].move_absolute(z, Units.LENGTH_MILLIMETRES, False)

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

    def StopPan(self):
        self._axisList[self.xSettings.deviceIndex].stop(False)
        self._axisList[self.ySettings.deviceIndex].stop(False)
        self._axisList[self.zSettings.deviceIndex].stop(False)

    def GetDeviceList(self) -> typing.List[typing.Tuple[str, str]]:
        return [(comport.device, comport.description) for comport in serial.tools.list_ports.comports()]
