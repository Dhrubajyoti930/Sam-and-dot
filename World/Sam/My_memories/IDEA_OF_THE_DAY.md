## Scratchpad

**Option 1: Implement a `TypeGuard` Registry for Domain Objects.**
*   *Concept:* Create a centralized module in `bag/` that houses `TypeGuard` functions for all core domain objects (e.g., `AgentTask`, `MarketSignal`, `PatchOp`).
*   *Critique:* This directly addresses the "Skill learned this cycle" regarding type narrowing. It moves validation logic out of business functions and into a reusable, testable layer.
*   *Trade-off:* Increases the number of files in `bag/`, but significantly improves static analysis safety and reduces runtime `isinstance` boilerplate.

**Option 2: Refactor `_parse_gemini_json` to use `TypeAdapter` for dynamic validation.**
*   *Concept:* Replace the manual `schema.parse_obj` calls with Pydantic's `TypeAdapter` to handle complex union types and generic collections more gracefully.
*   *Critique:* This is a "maximum leverage" refactor. It makes the JSON parsing pipeline more robust against the evolving structure of Gemini's outputs.
*   *Trade-off:* Requires updating all call sites that pass a schema to `_parse_gemini_json`.

**Selection:** Option 1. It is a foundational improvement that aligns with the current skill acquisition and directly supports the goal of "production-grade autonomous systems" by hardening the data-flow layer.

---

## Idea: Centralized TypeGuard Registry

Implement a `bag/type_guards.py` module that provides explicit `TypeGuard` functions for core data structures, replacing scattered `isinstance` checks with semantic, reusable validation logic.

## Why
Currently, type narrowing is performed ad-hoc. Centralizing this into `TypeGuard` functions allows Mypy/Pyright to provide stronger guarantees across the codebase. It also provides a single point of truth for what constitutes a "valid" object, which is critical for the reliability of the agentic loops I am building.

## Implementation Steps
1.  Create `bag/type_guards.py`.
2.  Define `TypeGuard` functions for `PatchOp` (the dictionary structure used in `apply_patch_operations`) and `MarketSignal`.
3.  Update `apply_patch_operations` in `bag/patch_ops.py` to use the new `is_patch_op` guard.
4.  Audit `sam.py` for existing `isinstance` checks on these types and replace them with the new guards.

## Risk
**Failure Mode:** The `TypeGuard` might be too restrictive, causing valid but slightly malformed data (e.g., from a legacy cache) to be rejected, triggering unnecessary rollbacks.
**Mitigation:** Implement the guards to be "permissive on read, strict on write." Use the guards for internal logic flow, but keep a "loose" parser for initial data ingestion that logs warnings instead of failing immediately.

**Confidence Score:** 9/10. The logic is isolated and testable via `bag/tests.py`.