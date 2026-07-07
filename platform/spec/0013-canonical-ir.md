---
id: SPEC-0013
title: Canonical AST / Platform IR
version: 1.0.0
status: Frozen
owner: Platform Core
depends_on: ["SPEC-0002", "SPEC-0012"]
referenced_by: []
compatibility: Backward Compatible
since: 1.0
supersedes: null
tags: ["ast", "ir", "contract", "compiler"]
---

# Spec 0013: Canonical AST / Platform IR

## Status

Frozen

## Purpose

Define the canonical internal representation used by the generator to transform specifications into derived artifacts.

## Contract

The Platform IR is the semantic representation between parsing and emission.

It must be:

- versioned
- deterministic
- language-neutral
- stable enough for code generation and conformance

## Required Fields

- protocol
- index
- specs

## Required Spec Node Fields

- header
- body

## Validation Rules

- The IR protocol must be explicit.
- The IR must preserve spec ordering.
- The IR must derive from `platform/spec/index.yaml` and the spec files.
- No emitter may become a source of truth.

