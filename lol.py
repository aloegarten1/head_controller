from utils import itmp, head_device

def main():
    m1 = itmp.itmp_message.ITMPDescribeMessage(1, "")
    print(m1.to_dict())
    print(m1.to_hdlc(4))
    
    m2 = itmp.itmp_message.ITMPMessage.from_hdlc(b'~\x04\x83\x06\x01`\xf7~')
    print(m2)

    '''
    dev = itmp.itmp_serial.ITMPSerialDevice("COM4")
    dev.write(itmp.itmp_message.ITMPDescribeMessage(1, ""))
    print(dev.read())
    dev.close()
    '''

    head = head_device.HeadDevice("COM4")
    print(head.enable())
    print(head.mot1_go(-3500, 1000, 7000))
    print(head.mot1_go(0, 1000, 7000))


if __name__ == "__main__":
    main()
