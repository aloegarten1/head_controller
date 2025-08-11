import serial
import serial.tools.list_ports
import time


def list_serial_ports():
    ports = list(serial.tools.list_ports.comports())
    return [port.device for port in ports]


def open_serial_port(port: str, baudrate=115200, timeout=0.1) -> serial.Serial:
    ser = serial.Serial(port, baudrate=baudrate, timeout=timeout)
    time.sleep(2) 
    return ser
