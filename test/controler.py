import serial
import serial.tools.list_ports
import time
import cbor2


crc8_table = [
	0, 94,188,226, 97, 63,221,131,194,156,126, 32,163,253, 31, 65,
	157,195, 33,127,252,162, 64, 30, 95, 1,227,189, 62, 96,130,220,
	35,125,159,193, 66, 28,254,160,225,191, 93, 3,128,222, 60, 98,
	190,224, 2, 92,223,129, 99, 61,124, 34,192,158, 29, 67,161,255,
	70, 24,250,164, 39,121,155,197,132,218, 56,102,229,187, 89, 7,
	219,133,103, 57,186,228, 6, 88, 25, 71,165,251,120, 38,196,154,
	101, 59,217,135, 4, 90,184,230,167,249, 27, 69,198,152,122, 36,
	248,166, 68, 26,153,199, 37,123, 58,100,134,216, 91, 5,231,185,
	140,210, 48,110,237,179, 81, 15, 78, 16,242,172, 47,113,147,205,
	17, 79,173,243,112, 46,204,146,211,141,111, 49,178,236, 14, 80,
	175,241, 19, 77,206,144,114, 44,109, 51,209,143, 12, 82,176,238,
	50,108,142,208, 83, 13,239,177,240,174, 76, 18,145,207, 45,115,
	202,148,118, 40,171,245, 23, 73, 8, 86,180,234,105, 55,213,139,
	87, 9,235,181, 54,104,138,212,149,203, 41,119,244,170, 72, 22,
	233,183, 85, 11,136,214, 52,106, 43,117,151,201, 74, 20,246,168,
	116, 42,200,150, 21, 75,169,247,182,232, 10, 84,215,137,107, 53
]


def crc8_get_part(crc, data):
	return crc8_table[crc ^ data]

def crc8_get(data):
	crc = 0xFF

	for i in range(len(data)):
		crc = crc8_get_part(crc, data[i])
	return crc


def list_serial_ports():
    ports = list(serial.tools.list_ports.comports())
    return [port.device for port in ports]


def open_first_available_port(baudrate=115200, timeout=1):
    ports = list_serial_ports()
    if not ports:
        raise RuntimeError("No available COM-ports.")
    print(f"Found ports: {ports}")
    port = ports[-1]
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
    encoded_with_crc = bytes([4]) + encoded
    crc = crc8_get(encoded_with_crc)
    encoded_with_crc += bytes([crc])
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


def poll(serial_port):
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
