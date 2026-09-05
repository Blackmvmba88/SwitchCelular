"""QR/LAN pairing bootstrap helpers."""

from .descriptor import (
    PairingDescriptor,
    PairingDescriptorError,
    build_pairing_uri,
    create_pairing_descriptor,
    discover_local_ipv4,
    parse_pairing_uri,
)

__all__ = [
    "PairingDescriptor",
    "PairingDescriptorError",
    "build_pairing_uri",
    "create_pairing_descriptor",
    "discover_local_ipv4",
    "parse_pairing_uri",
]
