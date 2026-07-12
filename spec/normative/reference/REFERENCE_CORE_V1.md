# REFERENCE_CORE_V1

## Status

Candidate Freeze

## Purpose

Define how external reference sources correct aiming intent without controlling the pipeline directly.

## Reference Sources

- `imu_reference`
- `vision_reference`
- `screen_reference`
- `marker_reference`
- future references

## Rules

- Reference sources must implement the same interface.
- Reference correction is advisory and explicit.
- Reference confidence must be exposed to `context_core`.
- A missing reference must not break the pipeline.
