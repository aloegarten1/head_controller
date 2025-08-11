import ctypes
import time
import win32con
import win32file


class COMMTIMEOUTS(ctypes.Structure):
    _fields_ = [
        ("ReadIntervalTimeout", ctypes.c_uint),
        ("ReadTotalTimeoutMultiplier", ctypes.c_uint),
        ("ReadTotalTimeoutConstant", ctypes.c_uint),
        ("WriteTotalTimeoutMultiplier", ctypes.c_uint),
        ("WriteTotalTimeoutConstant", ctypes.c_uint),
    ]


class Win32SerialPort:
    __EV_RXCHAR = 0x0001
    __EV_RXFLAG = 0x0008

    def __init__(self, device_name: str, baudrate: int, read_timeout: float):
        self.device_path =  f'\\\\.\\{device_name}'
        self.read_timeout_ms = read_timeout

        self.handle = win32file.CreateFile(
            self.device_path,
            win32con.GENERIC_READ | win32con.GENERIC_WRITE,
            0,
            None,
            win32con.OPEN_EXISTING,
            0,
            None
        )

        self.__set_DCB(baudrate)

    def __set_DCB(self, baudrate: int):
        dcb = win32file.GetCommState(self.handle)
        dcb.BaudRate = baudrate
        dcb.ByteSize = 8
        dcb.Parity = win32con.NOPARITY
        dcb.StopBits = win32con.ONESTOPBIT
        dcb.fRtsControl = win32con.RTS_CONTROL_ENABLE
        dcb.fDtrControl = win32con.DTR_CONTROL_ENABLE
        win32file.SetCommState(self.handle, dcb)

        win32file.SetCommState(self.handle, dcb)

        self.__set_timeouts(1000)
    
    def __set_timeouts(self, write_timeout_ms: float):
        timeouts = COMMTIMEOUTS()
        timeouts.ReadIntervalTimeout = win32con.MAXDWORD
        timeouts.ReadTotalTimeoutMultiplier = 0
        timeouts.ReadTotalTimeoutConstant = 0
        timeouts.WriteTotalTimeoutMultiplier = 0
        timeouts.WriteTotalTimeoutConstant = write_timeout_ms

        result = ctypes.windll.kernel32.SetCommTimeouts(
            int(self.handle),
            ctypes.byref(timeouts)
        )

        if result == 0:
            raise ctypes.WinError()

    def write(self, packet: bytes) -> None:
        win32file.WriteFile(self.handle, packet)

    def read(self) -> bytes:
        data = bytes([])
        ts = time.time()
        tc = time.time()
        while (tc - ts < self.read_timeout_ms) and ((len(data) < 2) or (hex(data[-1]) != hex(0x7e))):
            rc, recieved = win32file.ReadFile(self.handle, 1)
            data += recieved
            tc = time.time()
        if (tc - ts > self.read_timeout_ms):
            print("TIMEOUT!")
            return bytes([0])
        if not data:
            print("EWEWFEWF")
        return data

    def close(self):
        win32file.CloseHandle(self.handle)
