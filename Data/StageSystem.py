from zaber_motion import Library
from zaber_motion.ascii import Connection
from zaber_motion.ascii.device import Axis
from zaber_motion import Units
import typing
from Util import Event
import serial.tools.list_ports
from serial.tools.list_ports_common import ListPortInfo

Library.enable_device_db_store()


class StageSystem:
    def __init__(self):
        self._axisList: typing.List[Axis] = []
        self.activeConnection: typing.Optional[Connection] = None
        self.activePortInfo: typing.Optional[ListPortInfo] = None
        self.OnDisconnect = Event()

        self.xIndex = 0
        self.yIndex = 1
        self.zIndex = 2

    def Connect(self, portInfo: ListPortInfo):
        if self.activeConnection is not None:
            self.activeConnection.close()
        self.activePortInfo = portInfo
        self.activeConnection = Connection.open_serial_port(self.activePortInfo.device)
        self.activeConnection.disconnected.subscribe(lambda alert: self.OnDisconnect.Invoke())
        self._axisList = [device.get_axis(1) for device in self.activeConnection.detect_devices()]

    def HomeAll(self):
        for axis in self._axisList:
            axis.settings.set("maxspeed", 1, Units.VELOCITY_INCHES_PER_SECOND)
            axis.home(False)

    def IsMoving(self):
        for axis in self._axisList:
            if axis.is_busy():
                return True
        return False

    def GetPosition(self):
        x = self._axisList[self.xIndex].get_position(Units.LENGTH_MILLIMETRES)
        y = self._axisList[self.yIndex].get_position(Units.LENGTH_MILLIMETRES)
        z = self._axisList[self.zIndex].get_position(Units.LENGTH_MILLIMETRES)
        return x, y, z

    def SetPosition(self, x=None, y=None, z=None):
        if x is not None:
            self._axisList[self.xIndex].move_absolute(x, Units.LENGTH_MILLIMETRES, False)
        if y is not None:
            self._axisList[self.yIndex].move_absolute(y, Units.LENGTH_MILLIMETRES, False)
        if z is not None:
            self._axisList[self.zIndex].move_absolute(z, Units.LENGTH_MILLIMETRES, False)

    def __del__(self):
        if self.activeConnection is not None:
            self.activeConnection.close()

    @staticmethod
    def GetDeviceList():
        return [comport for comport in serial.tools.list_ports.comports()]
