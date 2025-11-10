import unittest
from utils.itmp.utils import hdlc_byte_stuff

class TestHDLCByteStuff(unittest.TestCase):
    def test_byte_stuff_and_unstuff(self):
        data = b'\x04\x83\x06\x01`\xf7'
        stuffed = hdlc_byte_stuff.byte_stuff(data)
        unstuffed = hdlc_byte_stuff.unstuff_bytes(stuffed)
        self.assertEqual(data, unstuffed)

    def test_bytes2hdlc_format(self):
        payload = b'\x04\x83\x06\x01`\xf7'
        hdlc = hdlc_byte_stuff.bytes2hdlc(payload)
        self.assertEqual(hdlc[0], 0x7E)
        self.assertEqual(hdlc[-1], 0x7E)
        self.assertEqual(hdlc[1:-1], b'\x04\x83\x06\x01`\xf7')

if __name__ == '__main__':
    unittest.main()
