from __future__ import annotations

from dataclasses import dataclass
import secrets
import socket
import time
from urllib.parse import parse_qs, urlencode, urlparse


class PairingDescriptorError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class PairingDescriptor:
    host: str
    port: int = 41235
    nonce: str = ""
    expires_at: int | None = None
    version: int = 1
    transport: str = "udp"


def _validate_host(host: str) -> str:
    value = host.strip()
    if not value or len(value) > 253 or any(char.isspace() for char in value):
        raise PairingDescriptorError("invalid pairing host")
    return value


def _validate_descriptor(descriptor: PairingDescriptor, *, now: int | None = None) -> PairingDescriptor:
    if descriptor.version != 1:
        raise PairingDescriptorError(f"unsupported pairing version: {descriptor.version}")
    if descriptor.transport.lower() != "udp":
        raise PairingDescriptorError(f"unsupported pairing transport: {descriptor.transport}")
    _validate_host(descriptor.host)
    if not 1 <= descriptor.port <= 65535:
        raise PairingDescriptorError("pairing port must be between 1 and 65535")
    if len(descriptor.nonce) < 16 or not descriptor.nonce.replace("-", "").replace("_", "").isalnum():
        raise PairingDescriptorError("pairing nonce must be a URL-safe token of at least 16 characters")
    current = int(time.time()) if now is None else int(now)
    if descriptor.expires_at is not None and descriptor.expires_at <= current:
        raise PairingDescriptorError("pairing descriptor has expired")
    return descriptor


def build_pairing_uri(descriptor: PairingDescriptor) -> str:
    _validate_descriptor(descriptor)
    query: dict[str, str | int] = {
        "v": descriptor.version,
        "transport": descriptor.transport.lower(),
        "host": descriptor.host,
        "port": descriptor.port,
        "nonce": descriptor.nonce,
    }
    if descriptor.expires_at is not None:
        query["exp"] = descriptor.expires_at
    return f"blackmamba://pair?{urlencode(query)}"


def parse_pairing_uri(uri: str, *, now: int | None = None) -> PairingDescriptor:
    parsed = urlparse(uri)
    if parsed.scheme.lower() != "blackmamba" or parsed.netloc.lower() != "pair":
        raise PairingDescriptorError("pairing URI must use blackmamba://pair")

    params = parse_qs(parsed.query, strict_parsing=True)

    def required(name: str) -> str:
        values = params.get(name)
        if not values or not values[0]:
            raise PairingDescriptorError(f"missing pairing field: {name}")
        return values[0]

    try:
        version = int(required("v"))
        port = int(required("port"))
        expires_at = int(params["exp"][0]) if params.get("exp") else None
    except ValueError as exc:
        raise PairingDescriptorError("pairing descriptor contains an invalid numeric field") from exc

    descriptor = PairingDescriptor(
        version=version,
        transport=required("transport").lower(),
        host=_validate_host(required("host")),
        port=port,
        nonce=required("nonce"),
        expires_at=expires_at,
    )
    return _validate_descriptor(descriptor, now=now)


def discover_local_ipv4() -> str:
    """Best-effort LAN IPv4 discovery without sending application data."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("192.0.2.1", 9))
        address = sock.getsockname()[0]
        if address and not address.startswith("127."):
            return address
    except OSError:
        pass
    finally:
        sock.close()

    try:
        for candidate in socket.gethostbyname_ex(socket.gethostname())[2]:
            if candidate and not candidate.startswith("127."):
                return candidate
    except OSError:
        pass

    return "127.0.0.1"


def create_pairing_descriptor(
    *,
    host: str | None = None,
    port: int = 41235,
    ttl_seconds: int = 300,
    now: int | None = None,
) -> PairingDescriptor:
    if ttl_seconds <= 0:
        raise PairingDescriptorError("ttl_seconds must be positive")
    current = int(time.time()) if now is None else int(now)
    descriptor = PairingDescriptor(
        host=_validate_host(host or discover_local_ipv4()),
        port=port,
        nonce=secrets.token_urlsafe(18),
        expires_at=current + ttl_seconds,
    )
    return _validate_descriptor(descriptor, now=current)
