from __future__ import annotations

import math
import unittest

from core.aim_core import aim_frame_from_motion_packet
from core.protocol_core import MotionPacket


class AimPacketAdapterTests(unittest.TestCase):
    def test_identity_packet_maps_to_forward_z(self):
        packet = MotionPacket(
            version=1,
            sequence=7,
            timestamp_ns=123,
            orientation={"w": 1.0, "x": 0.0, "y": 0.0, "z": 0.0},
            angular_velocity={"x": 0.0, "y": 0.0, "z": 0.0},
            acceleration={"x": 0.0, "y": 0.0, "z": 9.81},
            capabilities=["CAPABILITY_ORIENTATION"],
        )

        frame = aim_frame_from_motion_packet(packet)

        self.assertEqual(frame.timestamp_ns, 123)
        self.assertEqual(frame.forward_vector, (0.0, 0.0, 1.0))
        self.assertEqual(frame.confidence, 1.0)
        self.assertEqual(frame.reference_state["sequence"], 7)

    def test_adapter_normalizes_quaternion(self):
        packet = MotionPacket(
            version=1,
            sequence=1,
            timestamp_ns=1,
            orientation={"w": 2.0, "x": 0.0, "y": 0.0, "z": 0.0},
            angular_velocity={"x": 0.0, "y": 0.0, "z": 0.0},
            acceleration={"x": 0.0, "y": 0.0, "z": 0.0},
            capabilities=["CAPABILITY_ORIENTATION"],
        )

        frame = aim_frame_from_motion_packet(packet)
        magnitude = math.sqrt(
            frame.quaternion.w ** 2
            + frame.quaternion.x ** 2
            + frame.quaternion.y ** 2
            + frame.quaternion.z ** 2
        )
        self.assertAlmostEqual(magnitude, 1.0)

    def test_zero_quaternion_is_rejected(self):
        packet = MotionPacket(
            version=1,
            sequence=1,
            timestamp_ns=1,
            orientation={"w": 0.0, "x": 0.0, "y": 0.0, "z": 0.0},
            angular_velocity={"x": 0.0, "y": 0.0, "z": 0.0},
            acceleration={"x": 0.0, "y": 0.0, "z": 0.0},
        )

        with self.assertRaises(ValueError):
            aim_frame_from_motion_packet(packet)


if __name__ == "__main__":
    unittest.main()
