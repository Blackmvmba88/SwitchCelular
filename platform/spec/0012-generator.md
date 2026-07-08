---
id: SPEC-0012
title: Generator
version: 1.0.0
status: Frozen
owner: Platform Core
depends_on: ["SPEC-0001", "SPEC-0002"]
referenced_by: []
compatibility: Backward Compatible
since: 1.0
supersedes: null
tags: ["generator", "ast", "compiler"]
---

# Spec 0012: Generator

## Status

Frozen

## Purpose

Define the specification compiler that turns platform specs into a canonical AST and derived artifacts.

## Pipeline

- Parser
- Semantic Validation
- Platform IR
- Emitters
- Conformance
- Compatibility Reports

## Requirements

- deterministic output
- single source of truth
- no handwritten bindings
- no direct implementation-to-implementation generation
