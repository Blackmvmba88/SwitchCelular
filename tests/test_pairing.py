from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.pairing_core import (
    PairingDescriptor,
    PairingDescriptorError,
    build_pairing_uri,
    create_pairing_descriptor,
    parse_pairing_uri,
)


class PairingDescriptorTests(unittest.TestCase):
    def test_round_trip(self):
        descriptor = PairingDescriptor(
            host="192.168.1.20",
            port=41235,
            nonce="abcdefghijklmnop12345678",
            expires_at=4_000_000_000,
        )
        uri = build_pairing_uri(descriptor)
        parsed = parse_pairing_uri(uri, now=1_800_000_000)
        self.assertEqual(parsed, descriptor)

    def test_create_descriptor_is_short_lived_and_random(self):
        first = create_pairing_descriptor(host="10.0.0.5", port=5000, ttl_seconds=300, now=1000)
        second = create_pairing_descriptor(host="10.0.0.5", port=5000, ttl_seconds=300, now=1000)
        self.assertEqual(first.expires_at, 1300)
        self.assertNotEqual(first.nonce, second.nonce)
        self.assertGreaterEqual(len(first.nonce), 16)

    def test_rejects_expired_descriptor(self):
        uri = (
            "blackmamba://pair?v=1&transport=udp&host=192.168.1.20&port=41235"
            "&nonce=abcdefghijklmnop&exp=1000"
        )
        with self.assertRaisesRegex(PairingDescriptorError, "expired"):
            parse_pairing_uri(uri, now=1001)

    def test_rejects_wrong_scheme(self):
        uri = (
            "https://pair?v=1&transport=udp&host=192.168.1.20&port=41235"
            "&nonce=abcdefghijklmnop&exp=4000000000"
        )
        with self.assertRaisesRegex(PairingDescriptorError, "blackmamba"):
            parse_pairing_uri(uri, now=1000)

    def test_rejects_unsupported_transport(self):
        uri = (
            "blackmamba://pair?v=1&transport=tcp&host=192.168.1.20&port=41235"
            "&nonce=abcdefghijklmnop&exp=4000000000"
        )
        with self.assertRaisesRegex(PairingDescriptorError, "transport"):
            parse_pairing_uri(uri, now=1000)

    def test_rejects_invalid_port(self):
        uri = (
            "blackmamba://pair?v=1&transport=udp&host=192.168.1.20&port=70000"
            "&nonce=abcdefghijklmnop&exp=4000000000"
        )
        with self.assertRaisesRegex(PairingDescriptorError, "port"):
            parse_pairing_uri(uri, now=1000)


if __name__ == "__main__":
    unittest.main()
