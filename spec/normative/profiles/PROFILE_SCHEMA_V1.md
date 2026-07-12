# PROFILE_SCHEMA_V1

## Identifier

PROFILE_SCHEMA_V1

## Version

1.0.0

## Status

Candidate Freeze

## Purpose

Define the declarative profile format used to tune motion behavior without embedding game logic in the core.

## Scope

- Motion tuning.
- Trigger mapping.
- Reference preferences.
- Limits and safety constraints.

## Non Goals

- Executable logic.
- Game-specific branching.
- Transport framing.
- Host adapter behavior.

## Top-Level Sections

- `id`
- `version`
- `device`
- `motion`
- `trigger`
- `smoothing`
- `mapping`
- `limits`
- `reference`
- `context`

## Normative Rules

- Profiles MUST be data.
- Profiles MUST be validated before use.
- Profiles MUST NOT contain executable logic.
- Profile changes SHOULD NOT require rebuilding the core.
- Profile behavior MUST remain compatible with the motion packet and pipeline state contracts.
- Profile schema changes MUST preserve declared compatibility status.

## Invariants

- `id` MUST be stable within a versioned profile family.
- `version` MUST be explicit.
- Each top-level section MUST be independently parseable.
