# PeripheralOS Validation

PeripheralOS uses validation to prevent implementation-driven architecture drift.

The validation layer checks that canonical contracts exist, that the specification index matches those contracts, and that fixtures behave as expected.

## Install

```bash
python -m pip install -r requirements-dev.txt
```

## Validate Everything

```bash
python platform/generator/peripheralos_validate.py all
```

## Validate Specs Only

```bash
python platform/generator/peripheralos_validate.py specs
```

## Validate Fixtures Only

```bash
python platform/generator/peripheralos_validate.py fixtures
```

## Run Conformance Tests

```bash
pytest platform/tests/conformance
```

## What Is Checked

### Spec Index

The validator checks that:

- `platform/spec/index.yaml` exists.
- Canonical contracts are registered.
- Each registered contract file exists.
- Each contract ID matches the index.
- Required fields exist in each contract.

### Plugin Manifest Fixture

The validator checks that:

- The valid plugin manifest passes schema validation.
- The invalid plugin manifest fails schema validation.

## CI

GitHub Actions runs validation on:

- push to `main`
- pull requests targeting `main`

Workflow file:

```text
.github/workflows/conformance.yml
```

## Governance Rule

If a contract changes, validation assets must change with it.

A change that modifies ABI, lifecycle, plugins, actions, transports, security, compatibility, or generation behavior must include one or more of:

- specification update
- schema update
- fixture update
- conformance test update
- compatibility report
