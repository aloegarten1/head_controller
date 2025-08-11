from  utils.itmp.utils import win_serial_port

def main():
    port = win_serial_port.Win32SerialPort("COM4", 115200, 1)
    port.write(b'~\x04\x83\x06\x01`\xf7~')
    print(port.read())
    port.write(b'~\x04\x84\x08\x01fenable\x80\x80~')
    print(port.read())
    port.write(b'~\x04\x84\x08\x01eadc/p\x80\xdb~')
    print(port.read())
    port.write(b'~\x04\x84\x08\x01hmot1/pos\x80-~')
    print(port.read())
    port.write(b'~\x04\x84\x08\x01kmot1/sensor\x80\xc4~')
    print(port.read())
    port.write(b'~\x04\x84\x08\x01gmot1/go\x839\x07\xcf\x19\x03 \x19\x13\x88!~')
    print(port.read())


if __name__ == "__main__":
    main()
