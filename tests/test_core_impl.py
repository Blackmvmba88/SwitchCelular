from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.calibration_core import tune_profile_from_metrics
from core.diagnostics_core import RegressionMetrics, benchmark_pipeline
from core.fusion_core import fuse_samples
from core.sensor_core import AndroidSensorEvent, SensorSample, ingest_android_events, normalize_sample
from core.profile_core import load_profile, validate_profile
from core.protocol_core import MotionPacket, decode_motion_packet, encode_motion_packet
from core.reference_core import ScreenReference, VisionDetection, apply_screen_reference, apply_vision_reference
from core.aim_core import build_aim_frame


class CoreImplementationTests(unittest.TestCase):
    def test_motion_packet_roundtrip(self):
        packet = MotionPacket(
            version=1,
            sequence=7,
            timestamp_ns=1_000_000,
            orientation={"w": 1.0, "x": 0.0, "y": 0.0, "z": 0.0},
            angular_velocity={"x": 0.0, "y": 0.0, "z": 0.0},
            acceleration={"x": 0.0, "y": 0.0, "z": 9.81},
            buttons=3,
            battery=88,
            flags=1,
            capabilities=["CAPABILITY_ORIENTATION"],
            reserved=[],
            extension_length=0,
        )
        encoded = encode_motion_packet(packet)
        decoded = decode_motion_packet(encoded)
        self.assertEqual(decoded, packet)
        self.assertEqual(json.loads(encoded.decode("utf-8"))["sequence"], 7)

    def test_profile_loader_and_validator(self):
        profile = load_profile(ROOT / "spec" / "examples" / "profile_example.yaml")
        issues = validate_profile(profile)
        self.assertEqual(profile.id, "pistol")
        self.assertEqual(profile.version, "1.0.0")
        self.assertEqual(issues, [])

    def test_profile_loader_rejects_missing_keys(self):
        temp = ROOT / "platform" / "generated" / "test-invalid-profile.yaml"
        temp.parent.mkdir(parents=True, exist_ok=True)
        temp.write_text("version: 1.0.0\n", encoding="utf-8")
        with self.assertRaises(Exception):
            load_profile(temp)

    def test_sensor_normalization(self):
        sample = SensorSample(timestamp_ns=42, sensor=" Gyroscope ", x=1, y=2, z=3, accuracy=0.5, status=" OK ")
        normalized = normalize_sample(sample)
        self.assertEqual(normalized.sensor, "gyroscope")
        self.assertEqual(normalized.status, "ok")
        self.assertEqual(normalized.x, 1.0)

    def test_android_sensor_ingest(self):
        samples = ingest_android_events(
            [
                AndroidSensorEvent(timestamp_ns=10, sensor_type="TYPE_GYROSCOPE", values=(0.1, 0.2, 0.3)),
                AndroidSensorEvent(timestamp_ns=11, sensor_type="TYPE_ACCELEROMETER", values=(0.0, 0.0, 9.81)),
            ]
        )
        self.assertEqual([sample.sensor for sample in samples], ["gyroscope", "accelerometer"])
        self.assertEqual(samples[0].timestamp_ns, 10)

    def test_fusion_from_samples(self):
        samples = [
            SensorSample(timestamp_ns=1, sensor="gyroscope", x=0.1, y=0.2, z=0.3),
            SensorSample(timestamp_ns=2, sensor="accelerometer", x=0.0, y=0.0, z=9.81),
            SensorSample(timestamp_ns=3, sensor="magnetometer", x=1.0, y=0.5, z=0.25),
        ]
        frame = fuse_samples(samples)
        self.assertEqual(frame.timestamp_ns, 3)
        self.assertGreaterEqual(frame.confidence, 0.0)
        self.assertLessEqual(frame.confidence, 1.0)
        self.assertAlmostEqual(
            (frame.quaternion.w**2 + frame.quaternion.x**2 + frame.quaternion.y**2 + frame.quaternion.z**2) ** 0.5,
            1.0,
            places=6,
        )

    def test_reference_sources_and_tuning(self):
        samples = [
            SensorSample(timestamp_ns=1, sensor="gyroscope", x=0.1, y=0.2, z=0.3),
            SensorSample(timestamp_ns=2, sensor="accelerometer", x=0.0, y=0.0, z=9.81),
            SensorSample(timestamp_ns=3, sensor="magnetometer", x=1.0, y=0.5, z=0.25),
        ]
        frame = build_aim_frame(fuse_samples(samples))
        vision_frame, vision_state = apply_vision_reference(frame, VisionDetection(monitor_visible=True, confidence=0.8, center_offset_px=(12.0, -4.0)))
        screen_frame, screen_state = apply_screen_reference(vision_frame, ScreenReference(visible=True, confidence=0.7, screen_center=(0.05, 0.02)))
        self.assertTrue(vision_state.correction_applied)
        self.assertTrue(screen_state.correction_applied)
        tuned_profile, recommendation = tune_profile_from_metrics(
            load_profile(ROOT / "profiles" / "pistol.yaml"),
            RegressionMetrics(p50_latency_ms=10.0, p95_latency_ms=25.0, p99_latency_ms=30.0, drift_score=0.2, sample_count=8),
        )
        self.assertLess(tuned_profile.motion["smoothing"]["alpha"], 0.82)
        self.assertGreater(recommendation.deadzone_yaw, 0.35)
        self.assertGreaterEqual(screen_frame.confidence, 0.0)

    def test_pipeline_benchmark_reports_metrics(self):
        benchmark = benchmark_pipeline("fusion", 5, lambda: fuse_samples([SensorSample(timestamp_ns=1, sensor="gyroscope", x=0.1, y=0.2, z=0.3)]))
        self.assertEqual(benchmark.name, "fusion")
        self.assertEqual(len(benchmark.samples_ms), 5)
        self.assertIsNotNone(benchmark.metrics)
        self.assertGreaterEqual(benchmark.metrics.p50_latency_ms, 0.0)


if __name__ == "__main__":
    unittest.main()
