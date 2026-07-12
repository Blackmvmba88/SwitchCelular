# HOST_ADAPTER_ABI_V1

## Identifier

HOST_ADAPTER_ABI_V1

## Version

1.0.0

## Status

Candidate Freeze

## Purpose

Define the interface used by desktop-side adapters that consume motion intent and emit host input.

## Scope

- Host-side input emission.
- Adapter lifecycle.
- OS-specific backend isolation.

## Non Goals

- Motion sensing.
- Protocol interpretation.
- Profile tuning.
- Game-specific mapping.

## Required Operations

- `initialize`
- `apply_motion`
- `apply_buttons`
- `flush`
- `shutdown`

## Normative Rules

- Host adapters MUST isolate operating system APIs.
- Host adapters MUST NOT reinterpret the protocol.
- Host adapters MUST NOT mutate Android-side state.
- Host adapters MAY target mouse, keyboard, virtual gamepad, or future plugins.
- Host adapters MUST preserve motion ordering.

## Invariants

- `initialize` MUST run before any motion is applied.
- `shutdown` MUST release host resources.
- `flush` MUST commit buffered input when buffering is used.
