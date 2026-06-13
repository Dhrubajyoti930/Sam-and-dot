## Scratchpad

### Option 1: Runtime Type Validation Decorator
*   **Concept:** Create a `@validate_types` decorator using `inspect.signature` to enforce type hints at runtime.
*   **Critique:** 
    *   *Pros:* Directly addresses the "Action Items" from the skill-learning phase; improves system robustness by catching type mismatches before they propagate.
    *   *Cons:* Runtime introspection has a performance cost. If applied to "hot" functions, it could introduce latency.
    *   *Feasibility:* High. `inspect.signature` is well-understood and fits perfectly into the existing `sam.py` utility set.

### Option 2: Automated Module Registry
*   **Concept:** Use `inspect.getmembers` to scan `workshop_bench/` for classes inheriting from a base `Agent` class, creating a dynamic registry.
*   **Critique:**
    *   *Pros:* Enables a plugin-based architecture, allowing me to add new agentic capabilities without modifying the core dispatcher.
    *   *Cons:* Increases complexity of the `workshop_bench/` structure. Requires careful handling of circular imports during the scan.
    *   *Feasibility:* Medium. Requires robust error handling to ensure a single broken module doesn't crash the entire registry scan.

**Decision:** Option 1 is more aligned with my current need for "deterministic data structures" and "schema engineering" mentioned in the market signals. It provides immediate value for debugging and stability.

---

## Idea: `@enforce_types` Decorator
Implement a decorator that uses `inspect.signature` to validate that arguments passed to a function match the type hints defined in the function signature.

## Why
As I move toward more complex agentic workflows, silent type errors are a primary source of non-deterministic failure. By enforcing types at the boundary, I catch logic errors early, reducing the need for complex debugging later in the pipeline.

## Implementation Steps
1.  Define `enforce_types(func)` in `sam.py`.
2.  Use `inspect.signature(func)` to map `*args` and `**kwargs` to the function's parameters.
3.  Iterate through the bound arguments and compare their types against `param.annotation`.
4.  Raise a `TypeError` with a descriptive message if a mismatch is found.
5.  Apply this decorator to `_parse_gemini_json` and `save_goals` as a pilot test.

## Risk
*   **Failure Mode:** The decorator may fail on complex types (e.g., `Union`, `Optional`, or generic collections like `list[str]`) if the check is too simplistic (e.g., using `isinstance` directly).
*   **Mitigation:** Use `typing.get_origin` and `typing.get_args` to handle generic types correctly, or restrict the decorator to simple types initially.
*   **Confidence Score:** 9/10.

---

### Action Plan
I will proceed with the implementation of the `@enforce_types` decorator. This directly supports the goal of "schema engineering" and ensures that my internal data handling remains predictable as I scale my agentic capabilities.