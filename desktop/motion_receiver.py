from __future__ import annotations

import argparse
from pathlib import Path
import socket
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.protocol_core import decode_motion_packet


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Listen for PeripheralOS MOTION_PACKET_V1 datagrams from the paired phone."
    )
    parser.add_argument("--host", default="0.0.0.0", help="Bind address (default: 0.0.0.0).")
    parser.add_argument("--port", type=int, default=41235, help="UDP port (default: 41235).")
    parser.add_argument("--count", type=int, default=0, help="Stop after N packets; 0 means run forever.")
    return parser


def format_packet(packet) -> str:
    orientation = packet.orientation
    return (
        f"seq={packet.sequence:>8} "
        f"buttons=0x{packet.buttons:02x} "
        f"battery={packet.battery:>3}% "
        f"q=({orientation['w']:+.4f}, {orientation['x']:+.4f}, "
        f"{orientation['y']:+.4f}, {orientation['z']:+.4f})"
    )


def main() -> int:
    args = build_parser().parse_args()
    if args.port not in range(1, 65536):
        raise SystemExit("port must be between 1 and 65535")
    if args.count < 0:
        raise SystemExit("count must be >= 0")

    received = 0
    print(f"PeripheralOS motion receiver listening on {args.host}:{args.port}/udp")
    print("Scan a matching pairing QR on the phone, then move it. Ctrl-C to stop.")

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind((args.host, args.port))
            while args.count == 0 or received < args.count:
                payload, address = sock.recvfrom(65535)
                try:
                    packet = decode_motion_packet(payload)
                except Exception as error:
                    print(f"drop {address[0]}:{address[1]} invalid packet: {error}", file=sys.stderr)
                    continue
                received += 1
                print(f"{address[0]}:{address[1]} {format_packet(packet)}")
    except KeyboardInterrupt:
        print("\nreceiver stopped")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
