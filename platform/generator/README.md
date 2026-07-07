# Generator

Deterministic specification compiler for PeripheralOS.

Pipeline:

1. Parse specs
2. Build AST
3. Validate model
4. Emit schemas and bindings
5. Emit docs and compatibility reports

The generator must use a single source of truth and a stable output order.

