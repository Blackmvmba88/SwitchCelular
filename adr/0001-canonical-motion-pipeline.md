# ADR-0001: Canonical Motion Pipeline

## Status

Accepted

## Context

SwitchCelular is becoming a platform for programmable peripheral motion rather than a single game-specific controller.
The architecture must remain stable across bindings, transports, and host adapters.

## Decision

The canonical pipeline is:

```text
Sensor
  ↓
Reference
  ↓
Space
  ↓
Context
  ↓
Aim
  ↓
Host Adapter
```

The meaning of each stage is fixed:

- `sensor_core` collects raw motion data.
- `reference_core` corrects aim using external references.
- `space_core` models physical relationships and transforms.
- `context_core` emits advisory recommendations only.
- `aim_core` represents pointing intent, not OS output.
- host adapters emit desktop input without redefining the protocol.

## Consequences

- Implementations can evolve independently as long as the pipeline contract remains intact.
- Changing transports does not require changing the protocol.
- Adding new reference sources does not change the meaning of aim intent.
- Profiles remain declarative data rather than executable logic.
- Conformance can be validated against a stable pipeline contract.

## Invariants

- Specifications define the pipeline, not code.
- Bindings must preserve the pipeline semantics.
- Breaking changes require a new versioned contract and a follow-up ADR.
