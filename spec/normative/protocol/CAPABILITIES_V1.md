# CAPABILITIES_V1

## Identifier

CAPABILITIES_V1

## Version

1.0.0

## Status

Candidate Freeze

## Purpose

Define how a device advertises what it can do without the host making assumptions.

## Scope

- Device capability advertisement.
- Session discovery.
- Feature negotiation.

## Non Goals

- Runtime tuning.
- Transport framing.
- Host adapter behavior.
- Game-specific logic.

## Capability Flags

- `CAPABILITY_ORIENTATION`
- `CAPABILITY_ACCELERATION`
- `CAPABILITY_GYROSCOPE`
- `CAPABILITY_MAGNETOMETER`
- `CAPABILITY_TRIGGER`
- `CAPABILITY_TOUCHPAD`
- `CAPABILITY_HAPTICS`
- `CAPABILITY_BATTERY`
- `CAPABILITY_CAMERA_REFERENCE`
- `CAPABILITY_SCREEN_REFERENCE`

## Normative Rules

- Capabilities MUST be explicit.
- Capabilities MUST be discoverable before streaming begins.
- Missing capabilities MUST be represented as absent, not inferred.
- New capabilities MUST be additive unless a new version is published.
- Capability sets MUST remain immutable during a session.

## Invariants

- A host MUST NOT assume a capability that was not advertised.
- A binding MUST preserve capability ordering and identifiers exactly as specified.
