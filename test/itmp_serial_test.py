from utils import itmp_serial


def test_itmp2hdlc():
    addr = 4
    packet1 = [itmp_serial.ITMPMessageType.CALL, 1, ""]
    res = itmp_serial.build_hdlc_from_itmp(4, packet1)

    print(res)


print(test_itmp2hdlc())
