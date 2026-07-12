# Generator

Deterministic specification compiler for PeripheralOS.

## Pipeline

1. Parse normative specs into a canonical AST.
2. Validate identifiers, references, invariants, and contract relationships.
3. Emit machine-checkable artifacts.
4. Emit schemas, docs, and compatibility reports.
5. Emit bindings only after the AST and schemas are stable.

## Rules

- The generator MUST use a single source of truth.
- The generator MUST preserve stable output order.
- The generator MUST validate the spec before emitting artifacts.
- The generator MUST NOT infer missing contract semantics from implementation code.
