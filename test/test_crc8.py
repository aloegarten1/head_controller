import unittest
from utils import crc8

class TestCRC8(unittest.TestCase):
    def test_known_crc(self):
        data = b'\x04\x83\x06\x01`'
        result = crc8.crc8_get(data)
        expected = 0xF7
        self.assertEqual(result, expected)
    
    def test_crc_identity(self):
        self.assertEqual(crc8.crc8_get(b''), 0xFF)

if __name__ == '__main__':
    unittest.main()
