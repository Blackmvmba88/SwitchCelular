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
├── spec/                    # Normative and informative specifications
├── core/                    # Motion and perception implementation packages
├── desktop/                 # Desktop host adapters and mappers
├── protocol/                # Canonical protocol bindings
├── profiles/                # Declarative runtime profiles
├── runtime/                 # Shared runtime orchestration
├── sdk/                     # Public SDK surface
├── transports/              # Transport backends
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

PeripheralOS is in foundation mode with an active first-playable phone-controller path.

The repository remains intentionally biased toward governance, architecture, and contract design, but the Android-to-desktop motion path now has a concrete MVP implementation under review.

## Project Direction

PeripheralOS is not a single app.

It is the platform layer for a future ecosystem of programmable peripherals: devices that can be described, validated, controlled, extended, and evolved without losing architectural control.

## First Playable Path

The first user-facing MVP is documented in [`docs/GUN_MODE_MVP.md`](./docs/GUN_MODE_MVP.md).

That path treats the phone as a motion pistol controller:

- short-lived LAN QR pairing
- Android sensor capture
- orientation fusion
- canonical `MOTION_PACKET_V1`
- UDP transport
- desktop packet receiver
- aim mapping through the `pistol` profile
- preview deltas before host control
- opt-in macOS relative mouse output
- touch `FIRE` forwarded as button bit `0x01`

The implementation keeps game logic out of core and remains profile-driven.

### Quick LAN Preview

```bash
python -m pip install -r desktop/requirements-pairing.txt
python desktop/pairing_qr.py --port 41235
python desktop/aim_preview.py --port 41235
```

Scan the generated QR on Android, open PeripheralOS, move the phone, and inspect mapped `dx/dy`. On macOS, only after preview looks correct, enable host control explicitly:

```bash
python desktop/aim_preview.py --port 41235 --mouse
```

The QR is discovery/bootstrap only in this MVP. UDP does not authenticate the peer; use the current path on a trusted LAN until the nonce is consumed by a real session handshake.

## Implementation Layout

The real implementation surface is intentionally separated from the normative platform layer:

- `core/` holds motion, aim, reference, space, context, protocol, diagnostics, and regression packages.
- `desktop/` holds host adapters and mapping logic.
- `protocol/` holds canonical protocol bindings derived from `spec/`.
- `profiles/` holds declarative profiles.
- `runtime/` holds shared orchestration.
- `transports/` holds transport backends.
- `sdk/` holds public API surfaces.

## Specification Freeze

The current architectural direction is to freeze the normative contract surface in `spec/` before expanding implementation work.

The immediate normative set is:

- `MOTION_PACKET_V1`
- `CAPABILITIES_V1`
- `PROFILE_SCHEMA_V1`
- `HOST_ADAPTER_ABI_V1`
- `PIPELINE_STATE_V1`
- `AIM_CORE_V1`
- `REFERENCE_CORE_V1`
- `SPACE_CORE_V1`
- `CONTEXT_CORE_V1`
- `CONFORMANCE_V1`

Canonical examples and error identifiers are also part of the freeze surface:

- `spec/examples/`
- `spec/errors/`

Standard governance documents are part of the freeze surface too:

- `spec/VERSION.md`
- `spec/CHANGELOG_SPEC.md`
- `spec/IMPLEMENTATION_GUIDE.md`
