from __future__ import annotations

import json
from dataclasses import asdict

from .packet import MotionPacket


def encode_motion_packet(packet: MotionPacket) -> bytes:
    payload = asdict(packet)
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def decode_motion_packet(payload: bytes | str) -> MotionPacket:
    if isinstance(payload, bytes):
        data = json.loads(payload.decode("utf-8"))
    else:
        data = json.loads(payload)
    return MotionPacket(
        version=int(data["version"]),
        sequence=int(data["sequence"]),
        timestamp_ns=int(data["timestamp_ns"]),
        orientation=dict(data["orientation"]),
        angular_velocity=dict(data["angular_velocity"]),
        acceleration=dict(data["acceleration"]),
        buttons=int(data.get("buttons", 0)),
        battery=int(data.get("battery", 0)),
        flags=int(data.get("flags", 0)),
        capabilities=[str(value) for value in data.get("capabilities", [])],
        reserved=list(data.get("reserved", [])),
        extension_length=int(data.get("extension_length", 0)),
    )
