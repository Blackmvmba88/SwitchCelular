# ADR 0003: Transport Abstraction

## Status

Accepted

## Decision

Transport is abstracted from the Runtime and replaceable independently.

## Reason

- enables UDP, BLE, USB, TCP, and future transports
- keeps execution logic transport-agnostic

