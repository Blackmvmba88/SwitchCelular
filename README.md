# PeripheralOS

PeripheralOS is a governance-first execution platform for programmable peripherals.

It defines how programmable devices, runtimes, transports, plugins, actions, and implementations evolve without hidden architecture, undocumented behavior, or implementation-driven contracts.

## Mission

PeripheralOS exists to make peripheral computing programmable, auditable, portable, and safe.

The platform separates **what the system is** from **how any specific implementation runs it**.

- Specifications define the platform.
- ADRs define accepted architectural decisions.
- RFCs define proposed evolution.
- Schemas define machine-checkable contracts.
- Implementations conform to the platform; they do not redefine it.

## Core Principle

> Architecture must be explicit before implementation becomes authoritative.

No architectural rule should exist only in source code, comments, prototypes, or tribal knowledge.

## Repository Map

```text
.
├── CONSTITUTION.md          # Normative platform authority
├── ROADMAP.md               # Governance milestones and execution phases
├── README.md                # Project overview and onboarding map
├── adr/                     # Accepted architectural decisions
├── rfcs/                    # Proposed platform changes
├── schemas/                 # Machine-checkable contracts
└── platform/                # Normative platform layer
    ├── spec/                # Canonical specification index
    ├── generator/           # Deterministic binding/compiler surface
    ├── bindings/            # Generated outputs
    └── tests/               # Conformance and compatibility suites
```

## Platform Layers

PeripheralOS is organized around three layers:

| Layer | Purpose | Authority |
| --- | --- | --- |
| Governance | Constitution, ADRs, RFCs, roadmap | Defines how decisions are made |
| Specification | ABI, lifecycle, security, actions, transports, plugins | Defines what implementations must follow |
| Execution | Runtime, SDKs, plugins, transports, devices | Executes contracts without redefining them |

## Governance Model

PeripheralOS follows a strict governance order:

1. **Constitution** — permanent platform principles.
2. **Specifications** — normative contracts.
3. **ADRs** — accepted architectural decisions.
4. **RFCs** — proposed changes before acceptance.
5. **Schemas** — validation surfaces for machine enforcement.
6. **Implementations** — conforming runtime and device code.
7. **Tests** — conformance, compatibility, and regression proof.

## Non-Negotiable Rules

### No Hidden Architecture

Any architectural rule that affects compatibility, security, runtime behavior, ABI, lifecycle, plugin boundaries, or transport semantics must be documented in the platform layer.

### Specification Ownership

Every implementation module must map to an official specification.

If no specification exists, the implementation must not become authoritative until an RFC or ADR defines the missing contract.

### Compatibility Before Convenience

Breaking changes must be detected, documented, justified, and approved before they reach implementations.

### Deterministic Generation

Generated bindings and derived contracts must be reproducible from the canonical specification index.

## Foundation Freeze

The current milestone is **Phase 0: Foundation Freeze**.

The goal is to lock the platform foundation before implementation work accelerates.

Exit criteria:

- No architectural uncertainty remains.
- ABI v1 has a defined contract and validation fixtures.
- Runtime lifecycle is specified.
- Plugin, action, transport, and security models are specified.
- ADR and RFC processes are documented.
- Conformance and compatibility test structure exists.
- Implementation work does not alter platform contracts.

## Initial Execution Surfaces

PeripheralOS is designed to support multiple execution targets:

- Android peripheral control
- Desktop orchestration
- Embedded controllers
- Audio-reactive hardware
- DMX / lighting systems
- Sensor and actuator networks
- Remote-control and automation devices
- Future SDK and plugin ecosystems

## Development Workflow

Before implementing a feature:

1. Check whether a specification exists.
2. If not, open an RFC.
3. If accepted, record the decision as an ADR when architectural.
4. Update schemas or fixtures when contracts change.
5. Add conformance or compatibility tests.
6. Implement only after the contract is explicit.

## Current Status

PeripheralOS is in foundation mode.

The repository is intentionally biased toward governance, architecture, and contract design before runtime implementation.

## Project Direction

PeripheralOS is not a single app.

It is the platform layer for a future ecosystem of programmable peripherals: devices that can be described, validated, controlled, extended, and evolved without losing architectural control.
