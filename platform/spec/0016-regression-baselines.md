---
id: SPEC-0016
title: Regression Baselines / Trace Drift
version: 1.0.0
status: Frozen
owner: Platform Core
depends_on: ["SPEC-0015"]
referenced_by: []
compatibility: Backward Compatible
since: 1.0
supersedes: null
tags: ["regression", "baseline", "trace", "ci"]
---

# Spec 0016: Regression Baselines / Trace Drift

## Status

Frozen

## Purpose

Define the baseline model used to detect trace drift, hash drift, and regression changes in virtual campaigns.

## Contract

Baselines must:

- freeze expected trace hashes
- compare current campaign outputs against reference snapshots
- classify drift
- report compatibility impact

## Required Outputs

- baseline snapshot
- trace drift report
- regression status

