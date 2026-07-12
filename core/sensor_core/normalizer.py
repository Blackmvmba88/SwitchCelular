from __future__ import annotations

from collections.abc import Iterable

from .models import AndroidSensorEvent, SensorSample


ANDROID_SENSOR_MAP = {
    "TYPE_GYROSCOPE": "gyroscope",
    "TYPE_GYROSCOPE_UNCALIBRATED": "gyroscope",
    "TYPE_ACCELEROMETER": "accelerometer",
    "TYPE_LINEAR_ACCELERATION": "accelerometer",
    "TYPE_MAGNETIC_FIELD": "magnetometer",
    "TYPE_MAGNETIC_FIELD_UNCALIBRATED": "magnetometer",
}


def normalize_android_event(event: AndroidSensorEvent) -> SensorSample:
    sensor = ANDROID_SENSOR_MAP.get(event.sensor_type.upper(), event.sensor_type.strip().lower())
    x, y, z = event.values
    return SensorSample(
        timestamp_ns=int(event.timestamp_ns),
        sensor=sensor,
        x=float(x),
        y=float(y),
        z=float(z),
        accuracy=None if event.accuracy is None else float(event.accuracy),
        status=event.status.strip().lower(),
    )


def normalize_sample(sample: SensorSample) -> SensorSample:
    sensor = sample.sensor.strip().lower()
    status = sample.status.strip().lower() if sample.status else "ok"
    return SensorSample(
        timestamp_ns=int(sample.timestamp_ns),
        sensor=sensor,
        x=float(sample.x),
        y=float(sample.y),
        z=float(sample.z),
        accuracy=None if sample.accuracy is None else float(sample.accuracy),
        status=status,
    )


def normalize_samples(samples: list[SensorSample]) -> list[SensorSample]:
    return [normalize_sample(sample) for sample in samples]


def ingest_android_events(events: Iterable[AndroidSensorEvent]) -> list[SensorSample]:
    return [normalize_sample(normalize_android_event(event)) for event in events]
