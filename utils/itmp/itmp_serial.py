from .itmp_message import ITMPMessage
from .utils.win_serial_port import Win32SerialPort

class ITMPSerialDevice:
    def __init__(self, device_name: str, baudrate: int = 115200, read_timeout: int = 1):
        self.port_path = f'\\\\.\\{device_name}'
        self.read_timeout = read_timeout
        self.port = Win32SerialPort(self.port_path, baudrate, self.read_timeout)

    def write(self, message: "ITMPMessage") -> None:
        data = message.to_hdlc()
        self.port.write(data)

    def read(self) -> "ITMPMessage":
        raw_data = self.port.read()
        if raw_data:
            return ITMPMessage.from_hdlc(raw_data)
        return None

    def close(self) -> None:
        self.port.close()
