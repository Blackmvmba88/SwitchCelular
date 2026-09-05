# RFC 0001: QR LAN Pairing Bootstrap

## Status

Proposed

## Summary

Define a small, versioned QR payload that lets a phone discover a PeripheralOS desktop endpoint without manually typing an IP address or port.

The first implementation targets the local network and UDP. The QR payload is a bootstrap descriptor, not a replacement for transport authentication.

## Motivation

The phone-controller MVP should feel like a peripheral, not a network administration exercise.

Expected user flow:

1. Start the PeripheralOS desktop receiver.
2. Desktop discovers its LAN address and creates a short-lived pairing descriptor.
3. Desktop renders that descriptor as a QR code.
4. The user scans the QR code on Android.
5. Android opens PeripheralOS through a deep link and preloads the UDP endpoint.
6. The user confirms connection before motion packets are emitted.

No IP address or port entry is required in the normal path.

## Pairing URI v1

Canonical form:

```text
blackmamba://pair?v=1&transport=udp&host=192.168.1.20&port=41235&nonce=<urlsafe-token>&exp=<unix-seconds>
```

### Required fields

- `v`: descriptor version. v1 MUST be `1`.
- `transport`: v1 MUST be `udp`.
- `host`: LAN IPv4/IPv6 address or hostname accepted by the receiver transport.
- `port`: integer from 1 through 65535.
- `nonce`: short-lived URL-safe random bootstrap token.

### Optional fields

- `exp`: UNIX timestamp in seconds after which the descriptor MUST be rejected.

## Validation rules

Android MUST reject a descriptor when any of the following is true:

- URI scheme is not `blackmamba`.
- URI authority is not `pair`.
- version is unsupported.
- transport is unsupported.
- host is missing, contains whitespace, or exceeds 253 characters.
- port is outside `1..65535`.
- nonce is missing or shorter than 16 characters.
- `exp` is present and already expired.

Unknown query parameters SHOULD be ignored for forward compatibility.

## Security model

The QR code reduces accidental endpoint selection and supplies bootstrap entropy, but scanning it does **not** by itself authenticate the UDP motion stream.

For the first playable MVP:

- the descriptor SHOULD expire quickly (default: five minutes),
- the nonce MUST be generated with a cryptographically secure random source,
- Android MUST require an explicit connect action before emitting motion,
- desktop SHOULD bind the pairing session to a single active phone once the handshake layer exists.

A later RFC will define authenticated session establishment and replay protection. This RFC intentionally does not add pairing metadata to `MOTION_PACKET_V1`.

## Compatibility

The descriptor is transport bootstrap metadata and MUST remain outside the canonical motion packet.

Future transports may reuse the descriptor with a new `transport` value after a specification or RFC defines their required endpoint fields.

## Implementation plan

1. Add a dependency-free pairing descriptor parser/builder to Python core.
2. Add a desktop command that renders the descriptor to SVG QR when the optional QR dependency is installed.
3. Register `blackmamba://pair` as an Android deep link.
4. Add an Android parser with the same validation rules.
5. Surface the parsed endpoint in Android UI state.
6. Connect the parsed endpoint to `UdpMotionClient` when the Android runtime wiring is completed.

## Non-goals

- Internet traversal.
- WebRTC signaling.
- BLE pairing.
- Authentication of every motion datagram.
- Camera implementation inside PeripheralOS v0.1.
