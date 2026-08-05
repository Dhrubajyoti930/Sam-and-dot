## Scratchpad

**Option 1: Feature Flag Registry Implementation**
*   **Concept:** Create a `bag/feature_flags.py` that manages a central registry of toggles, replacing scattered `if` statements with a `FlagManager` class.
*   **Critique:** High alignment with the "Feature Flags & Gradual Rollouts" skill. It centralizes control and allows for the "default-off" safety wrapper.
*   **Trade-off:** Adds a layer of abstraction that might be overkill for a small codebase, but essential for long-term stability.
*   **Feasibility:** High. It fits perfectly into the existing `workshop_bench` structure.

**Option 2: Semantic Deduplication Engine (Phase IV Objective)**
*   **Concept:** Implement a module that compares new `idea_of_the_day` proposals against `experiences.json` using vector similarity to prevent redundant development cycles.
*   **Critique:** Directly addresses the "Semantic Deduplication" objective. It improves the quality of Sam's growth by ensuring he doesn't re-solve the same problems.
*   **Trade-off:** Requires a dependency on a local vector store or simple embedding comparison, which adds complexity to the `bag/` environment.
*   **Feasibility:** Moderate. Requires careful handling of the `experiences` data structure.

**Decision:** I will proceed with **Option 1**. It provides the infrastructure necessary to safely implement Option 2 later. By building the flag registry now, I can wrap future experimental features (like the deduplication engine) in a "default-off" flag, minimizing risk.

---

## Idea: Centralized Feature Flag Registry
Implement a `FlagManager` in `bag/feature_flags.py` that provides a thread-safe, cached interface for toggling features, including a "default-off" safety mechanism.

## Why
My current codebase lacks a formal mechanism for gradual rollouts. As I move toward more complex agentic workflows, I need the ability to toggle experimental logic without risking the stability of the core `sam.py` loop. This aligns with the "Feature Flags & Gradual Rollouts" skill learned this cycle.

## Implementation Steps
1.  **Create `bag/feature_flags.py`**: Define a `FlagManager` class with a `get(flag_name: str, default: bool = False)` method.
2.  **Persistence**: Use a simple JSON file in `bag/` to store flag states, with an in-memory cache for performance.
3.  **Integration**: Update `sam.py` to import `FlagManager` and wrap the "Semantic Deduplication" logic (the next objective) in a `if FlagManager.is_enabled("semantic_dedup"):` block.
4.  **Testing**: Add a test case in `bag/tests.py` to verify that the flag registry correctly defaults to `False` when a key is missing.

## Risk
**Failure Mode:** The `FlagManager` could become a single point of failure if the JSON file becomes corrupted or inaccessible, causing the entire system to default to "off" and potentially disabling critical functionality.
**Mitigation:** Implement a "fail-safe" mode where the `FlagManager` logs a critical error to `sam.py` but returns the hardcoded `default` value, ensuring the system remains operational even if the flag registry is unreachable.

**Confidence Score:** 9/10