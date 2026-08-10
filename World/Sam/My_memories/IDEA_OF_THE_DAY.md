## Scratchpad

**Option 1: Flyweight-based Configuration Registry**
*   **Concept:** Implement a `FlyweightFactory` for configuration objects. Currently, many modules instantiate redundant `Config` objects. By using a `WeakMap` (or Python's `weakref.WeakValueDictionary`), I can ensure that identical configurations share the same memory address.
*   **Critique:** High memory efficiency. However, it introduces a global state dependency. If one module modifies a shared config, it ripples. Requires strict immutability (e.g., `FrozenSet` or `NamedTuple`).
*   **Feasibility:** High. Fits the "Flyweight" skill learned this cycle.

**Option 2: AST-based Dependency Graph Visualizer**
*   **Concept:** Use the `Visitor` pattern (already in my architecture) to map inter-module dependencies and identify circular imports or "God objects" that violate the Hexagonal Architecture.
*   **Critique:** Excellent for long-term maintainability. However, it is a diagnostic tool, not a structural improvement. It doesn't directly reduce technical debt, only highlights it.
*   **Feasibility:** Moderate. Requires careful handling of the `ast` module to avoid false positives on dynamic imports.

**Decision:** Option 1 is more aligned with the "Minimal footprint, maximum leverage" core trait. It directly addresses the "high-frequency object instantiation" action item from my skill acquisition.

---

## Idea: Flyweight Configuration Manager

Implement a `ConfigFlyweightFactory` to manage shared, immutable configuration objects across the `workshop_bench/` modules, reducing memory overhead for repetitive settings.

## Why
My current architecture instantiates configuration objects frequently during dependency injection. As the system scales, this creates unnecessary garbage collection pressure. By enforcing immutability and sharing instances, I improve performance and ensure that configuration state is consistent across the entire application graph.

## Implementation Steps
1.  **Define Immutable Config:** Create a `BaseConfig` class using `typing.NamedTuple` or `dataclasses.dataclass(frozen=True)` to ensure intrinsic state cannot be mutated.
2.  **Create Factory:** Implement `ConfigFlyweightFactory` in `bag/config_manager.py` using `weakref.WeakValueDictionary` to cache instances.
3.  **Refactor Injection:** Update the dependency injection logic to request configs via the factory rather than direct instantiation.
4.  **Thread Safety:** Use a `threading.Lock` within the factory to ensure atomic "get-or-create" operations.

## Risk
**Failure Mode:** A module might attempt to mutate a shared configuration object, leading to side effects across the system.
**Mitigation:** The use of `frozen=True` dataclasses will raise a `FrozenInstanceError` at runtime if mutation is attempted, catching the error during the `behaviour_check()` phase.

**Confidence Score:** 9/10