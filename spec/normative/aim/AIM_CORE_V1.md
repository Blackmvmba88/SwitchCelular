# AIM_CORE_V1

## Identifier

AIM_CORE_V1

## Version

1.0.0

## Status

Candidate Freeze

## Purpose

Define how device orientation becomes an aim intent.

## Scope

- Orientation-to-aim conversion.
- Forward vector estimation.
- Aim confidence and drift reporting.

## Non Goals

- Host input emission.
- Game-specific behavior.
- Transport framing.
- UI rendering.

## Output

- `timestamp`
- `quaternion`
- `forward_vector`
- `confidence`
- `drift`
- `reference_state`

## Normative Rules

- `aim_core` MUST represent pointing intent, not OS output.
- `aim_core` MAY use IMU, IMU plus magnetometer, or external reference correction.
- `aim_core` MUST remain independent from host input adapters.
- `forward_vector` MUST be normalized when emitted.

## Invariants

- `confidence` SHOULD be bounded between `0.0` and `1.0`.
- `drift` SHOULD be reported whenever a correction source is available.
