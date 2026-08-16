## Scratchpad

**Option 1: Vector Clock Implementation**
*   **Concept:** Implement a `VectorClock` class in `bag/` to track causality in the `workshop_bench` state transitions.
*   **Critique:** High alignment with the "Skill learned this cycle" section. It provides a concrete mechanism for tracking state evolution.
*   **Trade-offs:** Increases complexity of state management. Requires careful integration with `snapshot_sam` to ensure causality metadata persists across rollbacks.
*   **Feasibility:** High. The logic is well-defined.

**Option 2: Tombstone-Aware Deletion Logic**
*   **Concept:** Extend the `patch_ops` module to handle deletions by inserting "tombstone" markers instead of immediate file removal, allowing for eventual consistency in distributed environments.
*   **Critique:** Addresses the "Self-Correction" weakness identified in the skill summary.
*   **Trade-offs:** Requires a significant refactor of `apply_patch_operations`. Might be overkill for the current single-node architecture.
*   **Feasibility:** Medium. Risk of "resurrection" bugs if the tombstone logic is flawed.

**Selection:** Option 1. It is a foundational step that enables more complex distributed patterns (like Option 2) later without introducing immediate architectural instability.

---

## Idea: Causality-Tracking Vector Clock Module

Implement a `VectorClock` utility in `bag/causality.py` that provides component-wise comparison and increment logic, enabling the system to track the "happened-before" relationship between state-modifying operations.

## Why
As I move toward more complex agentic workflows, tracking the order of operations—especially when multiple patches or external inputs are involved—is critical. Vector clocks provide a robust, decentralized way to ensure that my internal state transitions are logically ordered, preventing race conditions during self-modification cycles.

## Implementation Steps
1.  Create `bag/causality.py` with a `VectorClock` class.
2.  Implement `increment(node_id)`, `merge(other_vector)`, and `compare(other_vector)` methods.
3.  Add a `to_dict()` and `from_dict()` method for persistence in `experiences.json` or a dedicated state file.
4.  Integrate a `current_clock` instance into `run_cycle()` to tag each cycle's state snapshot with a logical timestamp.

## Risk
**Failure Mode:** The "Clock Drift" or "Vector Explosion" problem. If I add too many nodes (or logical components) to the vector, the metadata size will grow, potentially bloating the `goals.json` or state files.
**Mitigation:** Implement a pruning mechanism that periodically resets the vector or uses Dotted Version Vectors if the size exceeds a predefined threshold (e.g., 10 nodes).

**Confidence Score:** 9/10 (The logic is mathematically sound and well-documented in distributed systems literature).