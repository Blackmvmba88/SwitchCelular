# CONTEXT_CORE_V1

## Status

Candidate Freeze

## Purpose

Define the advisory layer that evaluates device, environment, and session context.

## Responsibilities

- detect device traits
- estimate environment conditions
- score reference confidence
- recommend profile adjustments
- recommend tuning changes

## Rules

- `context_core` must not move the cursor.
- `context_core` must not interpret the protocol.
- `context_core` must not mutate upstream state in place.
- `context_core` may emit recommendations only.
