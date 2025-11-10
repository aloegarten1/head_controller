import logging
import serial.tools.list_ports

from utils import head_device


def set_logger() -> None:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] (%(filename)s:%(lineno)d): %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )


def print_devices(devs: list) -> None:
    for dev in devs:
        print(f"\t- [{dev.serial_number}] {dev.name} - {dev.description}")


def main():
    set_logger()
    logger = logging.getLogger()
    logger.log(logging.INFO, "Logger started.")

    
    devs = serial.tools.list_ports.comports()
    
    if (len(devs) == 0):
        logger.log(level=logging.INFO, msg="No serial device was found. Try to connect USB-device to you host.")
        return
    print("\nAvailable devices:")
    print_devices(devs)
    head = head_device.HeadDevice("COM4")

    print(head.descr(""))
    
    head.set_valves(1, 0)


if __name__ == "__main__":
    main()
