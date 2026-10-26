"""Minimal dependency-free UDP motion packet reference (not a mouse driver)."""
import json
import math
import socket
import time

MAX_PACKET_BYTES = 1024

def validate_packet(packet):
    if not isinstance(packet, dict) or set(packet) != {"version", "seq", "timestamp_ms", "yaw", "pitch", "roll"}:
        raise ValueError("invalid packet fields")
    if type(packet["version"]) is not int or packet["version"] != 1:
        raise ValueError("unsupported version")
    if type(packet["seq"]) is not int or not 0 <= packet["seq"] < 2**32:
        raise ValueError("invalid sequence")
    if type(packet["timestamp_ms"]) is not int or packet["timestamp_ms"] < 0:
        raise ValueError("invalid timestamp")
    for key in ("yaw", "pitch", "roll"):
        value = packet[key]
        if type(value) not in (int, float) or not math.isfinite(value):
            raise ValueError("invalid orientation")
    return packet

def encode_packet(seq, yaw, pitch, roll, timestamp_ms=None):
    packet = {"version": 1, "seq": seq,
              "timestamp_ms": int(time.time() * 1000) if timestamp_ms is None else timestamp_ms,
              "yaw": yaw, "pitch": pitch, "roll": roll}
    validate_packet(packet)
    encoded = json.dumps(packet, separators=(",", ":"), allow_nan=False).encode("utf-8")
    if len(encoded) > MAX_PACKET_BYTES:
        raise ValueError("packet too large")
    return encoded

def decode_packet(data):
    if not isinstance(data, bytes) or len(data) > MAX_PACKET_BYTES:
        raise ValueError("invalid datagram size")
    try:
        packet = json.loads(data.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid JSON datagram") from exc
    return validate_packet(packet)

def listen(host="127.0.0.1", port=8765):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind((host, port))
        while True:
            data, _address = sock.recvfrom(MAX_PACKET_BYTES + 1)
            try:
                yield decode_packet(data)
            except ValueError:
                continue

if __name__ == "__main__":
    for item in listen():
        print(item, flush=True)
