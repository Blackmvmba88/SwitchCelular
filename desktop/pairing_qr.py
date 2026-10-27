from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.pairing_core import build_pairing_uri, create_pairing_descriptor


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate a short-lived PeripheralOS phone pairing QR for the local UDP receiver."
    )
    parser.add_argument("--host", help="LAN host/IP advertised to the phone. Auto-detected when omitted.")
    parser.add_argument("--port", type=int, default=41235, help="UDP receiver port (default: 41235).")
    parser.add_argument("--ttl", type=int, default=300, help="Pairing descriptor lifetime in seconds (default: 300).")
    parser.add_argument("--output", default="pairing.svg", help="SVG QR output path (default: pairing.svg).")
    parser.add_argument("--print-only", action="store_true", help="Print the pairing URI without rendering a QR file.")
    return parser


def render_svg(uri: str, output: Path) -> None:
    try:
        import qrcode
        from qrcode.image.svg import SvgPathImage
    except ImportError as exc:
        raise RuntimeError(
            "QR rendering requires the optional dependency: "
            "python -m pip install -r desktop/requirements-pairing.txt"
        ) from exc

    qr = qrcode.QRCode(border=4)
    qr.add_data(uri)
    qr.make(fit=True)
    image = qr.make_image(image_factory=SvgPathImage)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)


def main() -> int:
    args = build_parser().parse_args()
    descriptor = create_pairing_descriptor(host=args.host, port=args.port, ttl_seconds=args.ttl)
    uri = build_pairing_uri(descriptor)

    print("PeripheralOS QR pairing")
    print(f"Endpoint: {descriptor.host}:{descriptor.port}/udp")
    print(f"Expires:  {descriptor.expires_at}")
    print(f"URI:      {uri}")

    if args.print_only:
        return 0

    output = Path(args.output)
    try:
        render_svg(uri, output)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        print("The pairing URI above is still valid and can be encoded by any QR renderer.", file=sys.stderr)
        return 2

    print(f"QR SVG:   {output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
