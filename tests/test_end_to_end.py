from __future__ import annotations

from pathlib import Path
import sys
import threading
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.aim_core import build_aim_frame
from core.calibration_core import tune_profile_from_metrics
from core.diagnostics_core import MotionTrace, record_stage, finalize_trace
from core.context_core import recommend_context
from core.fusion_core import fuse_samples
from core.profile_core import load_profile_by_id, load_profiles, validate_profiles
from core.reference_core import ReferenceState, apply_reference_correction
from core.sensor_core import AndroidSensorEvent, SensorSample, ingest_android_events, normalize_samples
from core.space_core import SpaceState, project_aim_to_space
from core.transport_core import UdpTransportConfig, receive_motion_packet, send_motion_packet
from core.protocol_core import MotionPacket
from desktop.mapper_core import map_aim_to_delta
from desktop.host.adapter import MemoryHostAdapter
from desktop.host.mouse import RelativeMouseAdapter


class EndToEndTests(unittest.TestCase):
    def test_end_to_end_motion_flow(self):
        profiles = load_profiles(ROOT / "profiles")
        validation = validate_profiles(profiles)
        self.assertIn("pistol", validation)
        self.assertEqual(validation["pistol"], [])

        android_samples = ingest_android_events(
            [
                AndroidSensorEvent(timestamp_ns=1, sensor_type="TYPE_GYROSCOPE", values=(0.1, 0.2, 0.3)),
                AndroidSensorEvent(timestamp_ns=2, sensor_type="TYPE_ACCELEROMETER", values=(0.0, 0.0, 9.81)),
                AndroidSensorEvent(timestamp_ns=3, sensor_type="TYPE_MAGNETIC_FIELD", values=(1.0, 0.5, 0.25)),
            ]
        )
        samples = normalize_samples(android_samples)
        fusion_frame = fuse_samples(samples)
        aim_frame = build_aim_frame(fusion_frame, {"source": "imu_reference"}, drift=0.05)
        corrected_frame, reference_state = apply_reference_correction(
            aim_frame,
            ReferenceState(source="vision_reference", confidence=0.9, correction_applied=True, reference_vector=(0.05, 0.02, 1.0)),
        )
        space_frame, space_state = project_aim_to_space(corrected_frame, SpaceState(monitor_distance_cm=80.0))
        profile = load_profile_by_id(ROOT / "profiles", "pistol")
        recommendation = recommend_context(space_frame, profile)
        delta, mapper_state = map_aim_to_delta(space_frame, profile)
        trace = MotionTrace(id="end-to-end")
        record_stage(trace, "sensor_ingest", 1, 2, samples=len(samples))
        record_stage(trace, "fusion", 2, 3, confidence=fusion_frame.confidence)
        record_stage(trace, "aim", 3, 4, drift=aim_frame.drift)
        record_stage(trace, "reference", 4, 5, source=reference_state.source)
        record_stage(trace, "space", 5, 6, distance=space_state.monitor_distance_cm)
        record_stage(trace, "mapper", 6, 8, dx=delta.dx, dy=delta.dy)
        finalize_trace(trace, drift_score=aim_frame.drift)
        self.assertIsNotNone(trace.metrics)
        tuned_profile, calibration_recommendation = tune_profile_from_metrics(profile, trace.metrics)

        packet = MotionPacket(
            version=1,
            sequence=1,
            timestamp_ns=space_frame.timestamp_ns,
            orientation={
                "w": space_frame.quaternion.w,
                "x": space_frame.quaternion.x,
                "y": space_frame.quaternion.y,
                "z": space_frame.quaternion.z,
            },
            angular_velocity={"x": 0.0, "y": 0.0, "z": 0.0},
            acceleration={"x": 0.0, "y": 0.0, "z": 9.81},
            buttons=1,
            battery=90,
            flags=0,
            capabilities=["CAPABILITY_ORIENTATION", "CAPABILITY_GYROSCOPE"],
            reserved=[],
            extension_length=0,
        )

        config = UdpTransportConfig(port=41235)
        received_packet: list[MotionPacket] = []

        def _receiver() -> None:
            received_packet.append(receive_motion_packet(config))

        thread = threading.Thread(target=_receiver, daemon=True)
        thread.start()
        send_motion_packet(packet, config)
        thread.join(timeout=2.0)

        self.assertTrue(received_packet)
        self.assertEqual(received_packet[0], packet)
        self.assertTrue(reference_state.correction_applied)
        self.assertEqual(space_state.monitor_distance_cm, 80.0)
        self.assertEqual(recommendation.profile_id, "pistol")
        self.assertIn("latency", calibration_recommendation.reason)
        self.assertLessEqual(trace.metrics.p50_latency_ms, trace.metrics.p95_latency_ms)
        self.assertGreater(tuned_profile.motion["smoothing"]["alpha"], 0.0)
        self.assertGreaterEqual(delta.dx, 0.0)
        self.assertGreaterEqual(delta.dy, 0.0)
        self.assertEqual(mapper_state.last_profile_id, "pistol")

    def test_memory_host_adapter(self):
        adapter = MemoryHostAdapter()
        adapter.initialize()
        adapter.apply_motion(2.5, -1.5)
        adapter.apply_buttons(1)
        adapter.flush()
        adapter.shutdown()
        self.assertEqual(adapter.motion_events, [(2.5, -1.5)])
        self.assertEqual(adapter.button_events, [1])
        self.assertFalse(adapter.state.initialized)

    def test_relative_mouse_adapter(self):
        class FakeMouseBackend:
            def __init__(self) -> None:
                self.calls: list[tuple[float, float]] = []

            def move_relative(self, dx: float, dy: float) -> None:
                self.calls.append((dx, dy))

        backend = FakeMouseBackend()
        adapter = RelativeMouseAdapter(backend=backend)
        adapter.initialize()
        adapter.apply_motion(3.0, -2.0)
        adapter.flush()
        adapter.shutdown()
        self.assertEqual(adapter.emitted, [(3.0, -2.0)])
        self.assertEqual(backend.calls, [(3.0, -2.0)])


if __name__ == "__main__":
    unittest.main()
