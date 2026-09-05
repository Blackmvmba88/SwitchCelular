from __future__ import annotations

import argparse
from pathlib import Path
import socket
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.aim_core import aim_frame_from_motion_packet
from core.profile_core import load_profile_by_id
from core.protocol_core import decode_motion_packet
from desktop.mapper_core import map_aim_to_delta


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Preview phone motion through PeripheralOS aim + mapper layers without moving the host cursor."
    )
    parser.add_argument("--host", default="0.0.0.0", help="Bind address (default: 0.0.0.0).")
    parser.add_argument("--port", type=int, default=41235, help="UDP port (default: 41235).")
    parser.add_argument("--profile", default="pistol", help="Profile id from profiles/ (default: pistol).")
    parser.add_argument("--count", type=int, default=0, help="Stop after N packets; 0 means run forever.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    profile = load_profile_by_id(ROOT / "profiles", args.profile)
    mapper_state = None
    received = 0

    print(f"PeripheralOS aim preview on {args.host}:{args.port}/udp profile={profile.id}")
    print("This is preview-only: the cursor will not move.")

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind((args.host, args.port))
            while args.count == 0 or received < args.count:
                payload, address = sock.recvfrom(65535)
                try:
                    packet = decode_motion_packet(payload)
                    aim_frame = aim_frame_from_motion_packet(packet)
                    delta, mapper_state = map_aim_to_delta(aim_frame, profile, mapper_state)
                except Exception as error:
                    print(f"drop {address[0]}:{address[1]}: {error}", file=sys.stderr)
                    continue

                received += 1
                print(
                    f"seq={packet.sequence:>8} "
                    f"dx={delta.dx:+.5f} dy={delta.dy:+.5f} "
                    f"buttons=0x{packet.buttons:02x} "
                    f"confidence={aim_frame.confidence:.2f}"
                )
    except KeyboardInterrupt:
        print("\npreview stopped")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
