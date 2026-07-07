# Roadmap

PeripheralOS evolves through governance gates.

Each phase must produce explicit contracts before implementation work becomes authoritative.

## Phase 0: Foundation Freeze

**Goal:** freeze the platform foundation before runtime and device implementation accelerate.

### Scope

- Constitution
- Specification index
- ADR process
- RFC process
- ABI v1
- Runtime lifecycle
- Plugin model
- Action model
- Transport model
- Security model
- Repository layout
- Conformance tests
- Compatibility tests
- Deterministic binding generation

### Exit Criteria

- No architectural uncertainty remains.
- Implementation work does not alter platform contracts.
- Every implementation surface has a specification owner.
- Breaking changes are detectable by compatibility checks.
- Conformance tests can distinguish valid and invalid implementations.

## Phase 1: Contract Engine

**Goal:** make the platform machine-checkable.

### Deliverables

- Canonical spec registry
- Schema validation CLI
- ABI fixture validator
- Compatibility report format
- Generated binding manifest
- Spec-to-binding generation contract

### Exit Criteria

- A contract can be validated without reading implementation code.
- Generated outputs are reproducible from platform specs.
- Invalid fixtures fail deterministically.

## Phase 2: Reference Runtime

**Goal:** create the first conforming runtime implementation.

### Deliverables

- Runtime lifecycle executor
- Action dispatcher
- Plugin loader
- Transport adapter interface
- Device capability registry
- Security policy enforcement hooks

### Exit Criteria

- Runtime passes conformance tests.
- Runtime behavior maps back to official specifications.
- Runtime errors are structured and contract-aware.

## Phase 3: SDK and Developer Surface

**Goal:** allow external modules to build against PeripheralOS without depending on internals.

### Deliverables

- SDK skeleton
- Plugin template
- Action template
- Transport template
- Developer docs
- Example peripheral module

### Exit Criteria

- A developer can build a conforming plugin from templates.
- Generated bindings are stable enough for SDK usage.
- SDK documentation references specifications instead of implementation internals.

## Phase 4: Device Implementations

**Goal:** connect PeripheralOS contracts to real programmable peripherals.

### Candidate targets

- Android control surface
- Embedded controller bridge
- Audio-reactive LED system
- DMX / lighting transport
- Sensor and actuator peripheral
- Remote-control interface

### Exit Criteria

- Each implementation declares its spec ownership.
- Each implementation passes the relevant conformance suite.
- Device-specific behavior does not redefine platform contracts.

## Phase 5: Ecosystem Hardening

**Goal:** prepare PeripheralOS for public extension and long-term evolution.

### Deliverables

- Versioning policy
- Release process
- Compatibility matrix
- Security review checklist
- Governance automation
- Public contribution guide

### Exit Criteria

- Breaking changes require explicit review.
- Public contributions follow RFC / ADR flow.
- Release artifacts include compatibility evidence.
