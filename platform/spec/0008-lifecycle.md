---
id: SPEC-0008
title: Runtime Lifecycle
version: 1.0.0
status: Frozen
owner: Platform Core
depends_on: ["SPEC-0002", "SPEC-0003", "SPEC-0005"]
referenced_by: []
compatibility: Backward Compatible
since: 1.0
supersedes: null
tags: ["lifecycle"]
---

# Spec 0008: Runtime Lifecycle

## Status

Stable

## Purpose

Define the canonical lifecycle for devices and plugins.

## Lifecycle

- discover
- pair
- authenticate
- handshake
- capabilities
- ready
- streaming
- disconnected
- reconnect
