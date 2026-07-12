from __future__ import annotations

import socket
from dataclasses import dataclass

from core.protocol_core import MotionPacket, decode_motion_packet, encode_motion_packet


@dataclass(slots=True)
class UdpTransportConfig:
    host: str = "127.0.0.1"
    port: int = 41234
    timeout_s: float = 0.5


class UdpTransportError(RuntimeError):
    pass


def send_motion_packet(packet: MotionPacket, config: UdpTransportConfig) -> bytes:
    payload = encode_motion_packet(packet)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.sendto(payload, (config.host, config.port))
    return payload


def receive_motion_packet(config: UdpTransportConfig) -> MotionPacket:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(config.timeout_s)
        sock.bind((config.host, config.port))
        data, _ = sock.recvfrom(65535)
    return decode_motion_packet(data)
