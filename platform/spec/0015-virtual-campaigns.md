---
id: SPEC-0015
title: Virtual Campaigns / Regression / Fuzzing
version: 1.0.0
status: Frozen
owner: Platform Core
depends_on: ["SPEC-0014"]
referenced_by: []
compatibility: Backward Compatible
since: 1.0
supersedes: null
tags: ["virtualization", "campaigns", "fuzzing", "regression"]
---

# Spec 0015: Virtual Campaigns / Regression / Fuzzing

## Status

Frozen

## Purpose

Define campaign execution over multiple deterministic scenarios with controlled fuzzing and regression snapshots.

## Contract

Campaigns must:

- run multiple scenarios
- support deterministic fuzzing
- emit regression snapshots
- fail when trace hashes change unexpectedly

## Required Outputs

- campaign summary
- per-scenario trace
- per-scenario hash
- regression snapshot

