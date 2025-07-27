import serial
import serial.tools.list_ports
import time
import cbor2


def list_serial_ports():
    ports = list(serial.tools.list_ports.comports())
    return [port.device for port in ports]


def open_first_available_port(baudrate=115200, timeout=1):
    ports = list_serial_ports()
    if not ports:
        raise RuntimeError("No available COM-ports.")
    print(f"Found ports: {ports}")
    port = ports[0]
    print(f"Using port: {port}")
    ser = serial.Serial(port, baudrate=baudrate, timeout=timeout)
    time.sleep(2) 
    return ser


def build_itmp_describe_packet(to_desrcibe: str):
    packet = {
        0: 6,
        1: 1,
        2: to_desrcibe,
        3: []
    }
    return cbor2.dumps(packet)


import cbor2

# Примерная таблица CRC8 (можно заменить на реализацию, если нужна другая полиномиальная модель)
CRC8_POLY = 0x07

def crc8(data: bytes, poly=CRC8_POLY):
    crc = 0x00
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
                crc = ((crc << 1) ^ poly) & 0xFF
            else:
                crc = (crc << 1) & 0xFF
    return crc


def byte_stuff(data: bytes):
    ESCAPE = 0x7D
    FLAG = 0x7E
    ESCAPE_XOR = 0x20

    stuffed = bytearray()
    for byte in data:
        if byte in (ESCAPE, FLAG):
            stuffed.append(ESCAPE)
            stuffed.append(byte ^ ESCAPE_XOR)
        else:
            stuffed.append(byte)
    return bytes(stuffed)


def build_itmp_call_packet(to_call: str, args: list):
    # Шаг 1: сформировать CBOR-пакет
    packet = [6, 1, ""]
    encoded = cbor2.dumps(packet)

    # Шаг 2: добавить CRC8
    crc = crc8(encoded)
    encoded_with_crc = bytes([4]) + encoded + bytes([crc])
    print(f"Preprocessed packet: {encoded_with_crc}")

    # Шаг 3: выполнить byte stuffing
    stuffed = byte_stuff(encoded_with_crc)

    # Опционально: обернуть в фрейм с маркерами начала и конца
    FLAG = 0x7E
    final_packet = bytes([FLAG]) + stuffed + bytes([FLAG])

    return final_packet


def read_response(serial_port: serial.Serial):
    time.sleep(0.1)
    raw = serial_port.read(1024)
    if not raw:
        print("Нет ответа.")
        return None
    print(f"Сырые данные ({len(raw)} байт): {raw.hex()}")
    try:
        return cbor2.loads(raw)
    except Exception as e:
        print(f"Ошибка десериализации CBOR: {e}")
        return None


def  poll(serial_port):
    raw = bytes(0)
    while not raw:
        print("Listening to COM...")
        raw = serial_port.read(1024)
    print(f"Сырые данные ({len(raw)} байт): {raw.hex()}")
    try:
        return cbor2.loads(raw)
    except Exception as e:
        print(f"Ошибка десериализации CBOR: {e}")
        return None



def  print_describe_response(resp):
    if not isinstance(resp, dict) or 4 not in resp:
        print("Invalid response or command list does not exist.")
        return

    print("\nComand list:")
    for cmd in resp[4]:
        path = cmd.get("path", "???")
        doc = cmd.get("doc", "")
        args = cmd.get("args", [])
        ret = cmd.get("ret", [])

        print(f"- {path}: {doc}")
        if args:
            print(f"  Arguments: {[a.get('name') for a in args]}")
        if ret:
            print(f"  Returns: {[r.get('name') for r in ret]}")
        print()


def main():
    try:
        ser = open_first_available_port()

        packet = build_itmp_call_packet("enable", [])
        print(f"Sending CALL request ({len(packet)} bytes): {packet.hex()}")

        ser.write(packet)
        response = poll(ser)

        if response:
            print_describe_response(response)
        else:
            print("Client did not respond.")

    except Exception as e:
        print(f"Err: {e}")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()


if __name__ == "__main__":
    main()
