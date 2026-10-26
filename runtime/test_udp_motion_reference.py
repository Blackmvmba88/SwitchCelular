"""Run with: python -m unittest discover -s runtime -p 'test_udp_motion_reference.py'"""
import math
import unittest
from udp_motion_reference import encode_packet, decode_packet

class PacketTests(unittest.TestCase):
    def test_round_trip(self):
        packet = decode_packet(encode_packet(3, 12.5, -4, 0, 123))
        self.assertEqual(packet["seq"], 3)
        self.assertEqual(packet["yaw"], 12.5)

    def test_reject_nan(self):
        with self.assertRaises(ValueError):
            encode_packet(1, math.nan, 0, 0, 123)

    def test_reject_bad_version(self):
        with self.assertRaises(ValueError):
            decode_packet(b'{"version":2,"seq":1,"timestamp_ms":0,"yaw":0,"pitch":0,"roll":0}')

    def test_reject_oversize(self):
        with self.assertRaises(ValueError):
            decode_packet(b"x" * 1025)

    def test_reject_bool_sequence(self):
        with self.assertRaises(ValueError):
            encode_packet(True, 0, 0, 0, 123)

if __name__ == "__main__":
    unittest.main()
