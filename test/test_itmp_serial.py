import unittest
from utils import itmp_serial
from utils.itmp_serial import ITMPMessageType
import cbor2

class TestITMPSerial(unittest.TestCase):
    def test_build_itmp_hdlc_call_packet(self):
        packet = itmp_serial.build_itmp_hdlc_call_packet(0x01, 42, "foo", [1, 2])
        self.assertTrue(packet.startswith(b'\x7E') and packet.endswith(b'\x7E'))

    def test_build_and_read_itmp(self):
        addr = 0x11
        msg_id = 42
        procedure = "do_something"
        args = [123, "abc"]

        built = itmp_serial.build_itmp_hdlc_call_packet(addr, msg_id, procedure, args)[1:]
        parsed = itmp_serial.read_itmp_hdlc_packet(built)
        
        self.assertEqual(parsed[0], addr)
        self.assertEqual(parsed[1][0], ITMPMessageType.CALL.value)
        self.assertEqual(parsed[1][1], msg_id)
        self.assertEqual(parsed[1][2], procedure)
        self.assertEqual(parsed[1][3], args)

if __name__ == '__main__':
    unittest.main()
