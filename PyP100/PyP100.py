from base64 import b64decode
from .auth_protocol import AuthProtocol


class Device:
    def __init__(self, address, email, password):
        self.address = address
        self.email = email
        self.password = password
        self.protocol = None

    def _initialize(self):
        try:
            self.protocol = AuthProtocol(self.address, self.email, self.password)
            self.protocol.Initialize()
        except Exception as e:
            raise Exception(f"Failed to initialize device: {e}")

    def request(self, method: str, params: dict = None):
        if not self.protocol:
            self._initialize()
        return self.protocol._request(method, params)

    def handshake(self):
        if not self.protocol:
            self._initialize()
        return

    def login(self):
        return self.handshake()

    def getDeviceInfo(self):
        return self.request("get_device_info")

    def _get_device_info(self):
        return self.request("get_device_info")

    def _set_device_info(self, params: dict):
        return self.request("set_device_info", params)

    def getDeviceName(self):
        data = self.getDeviceInfo()
        encodedName = data["nickname"]
        name = b64decode(encodedName)
        return name.decode("utf-8")


class Switchable(Device):
    def get_status(self) -> bool:
        return self._get_device_info()["device_on"]

    def set_status(self, status: bool):
        return self._set_device_info({"device_on": status})

    def turnOn(self):
        return self.set_status(True)

    def turnOff(self):
        return self.set_status(False)

    def toggleState(self):
        return self.set_status(not self.get_status())

    def turnOnWithDelay(self, delay):
        raise NotImplementedError()

    def turnOffWithDelay(self, delay):
        raise NotImplementedError()


class Metering(Device):
    def getEnergyUsage(self):
        raise NotImplementedError()


class Color(Device):
    def setBrightness(self, brightness):
        raise NotImplementedError()

    def setColorTemp(self, colortemp):
        raise NotImplementedError()

    def setColor(self, hue, saturation):
        raise NotImplementedError()


class P100(Switchable):
    pass
