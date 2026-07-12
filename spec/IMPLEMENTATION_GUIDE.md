# Implementation Guide

This guide explains how to implement a conforming SwitchCelular binding or runtime.

## Steps

1. Read `spec/VERSION.md`.
2. Read the normative contract set.
3. Load canonical examples.
4. Validate against the error catalog and conformance rules.
5. Implement the required conformance level.
6. Do not redefine the specification in code.

## Required Checks

- Packet serialization round-trip.
- Capability negotiation.
- Profile schema validation.
- Pipeline state transition validation.
- Host adapter ABI compliance.
- Regression trace replay.

## Output Expectations

- Stable bindings.
- Deterministic serialization.
- Explicit compatibility claims.
- Declared conformance level.
