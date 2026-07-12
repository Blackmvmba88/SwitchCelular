# PIPELINE_STATE_V1

## Identifier

PIPELINE_STATE_V1

## Version

1.0.0

## Status

Candidate Freeze

## Purpose

Define the immutable state flow shared by the pipeline.

## Scope

- Pipeline lifecycle.
- Stage input and output state.
- Session state progression.
- Reproducible capture and playback.

## State Machine

```text
IDLE
  ↓
CONNECTING
  ↓
READY
  ↓
TRACKING
  ↘
   PAUSED
  ↘
   ERROR
```

## State Chain

- `SensorState`
- `FusionState`
- `CalibrationState`
- `AimFrame`
- `ReferenceState`
- `SpaceState`
- `ContextState`
- `ProfileState`
- `MotionPacket`
- `HostMotionState`

## Normative Rules

- Each stage MUST consume one state and produce a new one.
- Stages MUST NOT mutate upstream outputs in place.
- State MUST be reproducible for regression capture and playback.
- Pipeline state changes MUST require explicit versioning.
- State transitions MUST be valid according to the documented state machine.

## Invariants

- `IDLE` MUST precede `CONNECTING`.
- `READY` MUST precede `TRACKING`.
- `TRACKING` MAY transition to `PAUSED`.
- `TRACKING` MAY transition to `ERROR`.
- `ERROR` MAY transition back to `CONNECTING`.
