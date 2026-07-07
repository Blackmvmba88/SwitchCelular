# PeripheralOS Architecture

PeripheralOS is a specification-led platform for programmable peripherals.

The architecture is designed around one rule:

> Implementations execute contracts. They do not invent them.

## Architectural Intent

PeripheralOS separates governance, specification, validation, and execution so the platform can grow without losing control.

The system must support:

- programmable devices
- runtime orchestration
- plugin extension
- transport abstraction
- action dispatch
- schema validation
- compatibility tracking
- deterministic code generation

## Authority Stack

```text
Constitution
    ↓
Specifications
    ↓
ADRs
    ↓
RFCs
    ↓
Schemas
    ↓
Generated bindings
    ↓
Reference runtime
    ↓
Device implementations
```

Higher layers constrain lower layers.
Lower layers must not silently redefine higher layers.

## Main Subsystems

### 1. Governance Layer

Defines how the platform changes.

Owned by:

- `CONSTITUTION.md`
- `ROADMAP.md`
- `adr/`
- `rfcs/`

Responsibilities:

- define architectural authority
- record accepted decisions
- evaluate proposed changes
- prevent implementation-driven drift

### 2. Specification Layer

Defines what the platform is.

Owned by:

- `platform/spec/`
- `schemas/`

Responsibilities:

- ABI contracts
- runtime lifecycle
- plugin boundaries
- action semantics
- transport behavior
- security model
- compatibility rules

### 3. Generation Layer

Turns canonical specs into deterministic outputs.

Owned by:

- `platform/generator/`
- `platform/bindings/`

Responsibilities:

- read specification index
- validate source contracts
- emit generated bindings
- preserve reproducibility
- prevent manual edits to generated outputs

### 4. Validation Layer

Proves whether something conforms.

Owned by:

- `platform/tests/conformance/`
- `platform/tests/compatibility/`

Responsibilities:

- validate fixtures
- detect breaking changes
- verify implementation behavior
- produce compatibility reports

### 5. Execution Layer

Runs conforming implementations.

Future ownership:

- `runtime/`
- `sdk/`
- `plugins/`
- `transports/`
- `implementations/`

Responsibilities:

- execute runtime lifecycle
- load plugins
- dispatch actions
- bind transports
- expose device capabilities
- enforce security policy

## Contract Flow

```text
RFC proposes a change
    ↓
ADR accepts architecture when needed
    ↓
Spec updates canonical contract
    ↓
Schema validates machine-readable shape
    ↓
Generator emits bindings
    ↓
Tests verify conformance and compatibility
    ↓
Runtime or device implementation consumes contract
```

## Runtime Model

The reference runtime should eventually support this lifecycle:

```text
discover → validate → load → configure → start → execute → observe → stop → unload
```

Each phase must be specified before implementation becomes authoritative.

## Plugin Model

Plugins extend PeripheralOS without mutating the core.

A plugin must declare:

- identity
- version
- capabilities
- required permissions
- supported actions
- supported transports
- lifecycle hooks
- compatibility range

## Action Model

Actions are the platform's command surface.

An action must define:

- name
- input schema
- output schema
- side effects
- permission requirements
- error behavior
- compatibility guarantees

## Transport Model

Transports move actions and events between runtimes, devices, and controllers.

Possible transports:

- USB
- BLE
- Wi-Fi
- serial
- MIDI
- DMX bridge
- local IPC
- future network protocols

Each transport must specify:

- framing
- delivery guarantees
- timeout behavior
- error behavior
- security assumptions

## Security Model

Security is part of the platform contract, not an implementation detail.

The platform must define:

- permission boundaries
- trusted and untrusted plugins
- capability negotiation
- action authorization
- transport trust level
- safe failure behavior

## Compatibility Model

Compatibility must be measurable.

A change is breaking when it modifies contract behavior expected by conforming implementations.

Examples:

- removing a required field
- changing an action input type
- changing lifecycle order
- weakening validation guarantees
- changing transport error semantics

## Foundation Freeze Definition

Foundation Freeze is complete when:

- every core architectural surface has an owner
- every execution surface maps to a specification
- every breaking-change risk has a compatibility strategy
- conformance tests can reject invalid behavior
- runtime implementation can begin without redefining architecture

## Design Bias

PeripheralOS prefers:

- explicit contracts over implicit behavior
- deterministic generation over manual duplication
- governance before implementation
- compatibility over convenience
- specs before runtime code
- small stable interfaces over large unstable abstractions
