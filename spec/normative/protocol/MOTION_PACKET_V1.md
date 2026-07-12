# MOTION_PACKET_V1

## Identifier

MOTION_PACKET_V1

## Version

1.0.0

## Status

Candidate Freeze

## Purpose

Define the canonical packet shared by Android, transport, and desktop host layers.

## Scope

- Motion packet encoding.
- Session ordering.
- Capability advertisement.
- Forward-compatible extensions.

## Non Goals

- UI metadata.
- Game-specific metadata.
- Transport-specific framing.
- Host adapter behavior.

## Terminology

- `MUST`, `MUST NOT`, `SHALL`, `SHOULD`, `SHOULD NOT`, and `MAY` are to be interpreted as normative keywords.

## Normative Rules

- The packet MUST be transport-agnostic.
- The packet MUST be language-agnostic.
- The packet MUST be versioned.
- All numeric fields MUST have explicit types and units.
- Reserved fields MUST remain reserved for forward compatibility.
- Packet timestamps MUST be monotonic within a session.
- Quaternion payloads MUST be normalized before emission.
- Packet ordering MUST be preserved by the producer.

## Required Fields

- `version`
- `sequence`
- `timestamp_ns`
- `orientation`
- `angular_velocity`
- `acceleration`
- `buttons`
- `battery`
- `flags`
- `capabilities`
- `reserved`
- `extension_length`

## Compatibility Rules

- `v1.x` MAY add optional fields.
- `v2.0` MAY break compatibility.
- Serialization MUST be deterministic.
- Endianness MUST be documented by the binding implementation and treated as part of the contract.

## Invariants

- `version` MUST identify the packet contract version.
- `sequence` MUST increase monotonically within a session.
- `timestamp_ns` MUST be expressed in nanoseconds.
- `capabilities` MUST remain immutable during a session.
- `extension_length` MUST match the encoded extension payload length.
