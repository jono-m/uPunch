from Data.StageSystem import *
import time


class MockAxisSettings(AxisSettings):
    def __init__(self, deviceIndex):
        super().__init__(deviceIndex)
        self.position = 0
        self.goal = 0
        self.velocity = 0


class MockStageSystem(StageSystem):
    def __init__(self, hostWidget: QWidget):
        self.xSettings = MockAxisSettings(0)
        self.ySettings = MockAxisSettings(1)
        self.zSettings = MockAxisSettings(2)

        super().__init__(hostWidget)

        self._connected = False

        self._lastGetTime = None

        self._homed = False

    def Connect(self, portName: str):
        self._connected = True
        self._homed = False
        self.portName = portName

    def GetAxisName(self, axis: AxisSettings) -> str:
        return "Mock Axis"

    def IsConnected(self) -> bool:
        return self._connected

    def Disconnect(self):
        self._connected = False
        self.portName = "NOT CONNECTED"

    def HomeAll(self):
        self.xSettings.position = 0
        self.ySettings.position = 0
        self.zSettings.position = 0
        self._homed = True

    def IsHomed(self) -> bool:
        return self._homed

    def IsMoving(self) -> bool:
        isMoving = self.xSettings.velocity != 0 or \
                   self.ySettings.velocity != 0 or \
                   self.zSettings.velocity != 0
        return isMoving

    def GetPosition(self, axis: typing.Optional[AxisSettings] = None) -> \
            typing.Union[typing.Tuple[float, float, float], float]:
        current = time.time()
        if self._lastGetTime is None:
            self._lastGetTime = current
        deltaTime = current - self._lastGetTime

        self.UpdateVelocity(self.xSettings)
        self.UpdateVelocity(self.ySettings)
        self.UpdateVelocity(self.zSettings)

        self.MoveStep(self.xSettings, deltaTime)
        self.MoveStep(self.ySettings, deltaTime)
        self.MoveStep(self.zSettings, deltaTime)

        self._lastGetTime = current

        if axis is None:
            return self.xSettings.position, self.ySettings.position, self.zSettings.position
        elif isinstance(axis, MockAxisSettings):
            return axis.position
        else:
            return 0

    def UpdateVelocity(self, axis: MockAxisSettings):
        if axis.goal is not None:
            axis.goal = axis.ClampAxis(axis.goal)
            deltaPosition = axis.goal - axis.position

            # if we are at our goal, or our goal is in the opposite direction of our current velocity (i.e. overshoot)
            # then snap to the goal
            if deltaPosition == 0 or deltaPosition * axis.velocity < 0:
                axis.velocity = 0
                axis.position = axis.goal
            else:
                xDir = deltaPosition / abs(deltaPosition)
                axis.velocity = xDir * axis.maxSpeed

    def MoveStep(self, axis: MockAxisSettings, deltaTime: float):
        axis.position = axis.ClampAxis(axis.position + axis.velocity * deltaTime)

    def SetPosition(self, x=None, y=None, z=None):
        if self.IsMoving():
            return
        if x is not None:
            self.xSettings.goal = self.xSettings.ClampAxis(x)
            self.UpdateVelocity(self.xSettings)
        if y is not None:
            self.ySettings.goal = self.ySettings.ClampAxis(y)
            self.UpdateVelocity(self.ySettings)
        if z is not None:
            self.zSettings.goal = self.zSettings.ClampAxis(z)
            self.UpdateVelocity(self.zSettings)

    def FlushSettings(self, settings: AxisSettings):
        pass

    def PanAxis(self, axisSettings: AxisSettings, slowSpeed, direction):
        if self.IsMoving():
            return

        v = self.GetPanVelocity(axisSettings, slowSpeed, direction)
        if axisSettings == self.xSettings:
            self.xSettings.goal = None
            self.xSettings.velocity = v
        if axisSettings == self.ySettings:
            self.ySettings.goal = None
            self.ySettings.velocity = v
        if axisSettings == self.zSettings:
            self.zSettings.goal = None
            self.zSettings.velocity = v

    def StopPan(self):
        self.xSettings.velocity = 0
        self.ySettings.velocity = 0
        self.zSettings.velocity = 0

    def GetDeviceList(self) -> typing.List[typing.Tuple[str, str]]:
        return [("MCOM0", "Mock Device 0"),
                ("MCOM1", "Mock Device 1"),
                ("MCOM2", "Mock Device 2")]
