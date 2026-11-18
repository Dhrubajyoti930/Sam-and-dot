## Scratchpad

**Option 1: GraphRAG Integration for `knowledge_log.json`**
*   **Concept:** Transition from a flat JSON list to a graph-based structure (using `networkx` or `Qdrant`) to map relationships between learned skills.
*   **Critique:** High complexity. While it improves retrieval for Phase II (Spaced Repetition), it introduces a dependency on external graph libraries that might bloat the `bag/` directory.
*   **Feasibility:** Moderate. Requires refactoring `phase_ii_spaced_repetition` to handle graph traversal.

**Option 2: Markov-Chain-Based "Task Scheduler"**
*   **Concept:** Use the Markov Chain skill learned this cycle to model the transition between Sam's operational phases. Instead of a linear `run_cycle()`, use a transition matrix to determine if a cycle should prioritize "Deep Learning" vs "Refactoring" based on current system health (e.g., error rates in `log`).
*   **Critique:** Elegant and aligns with the new skill. It adds a layer of "stochastic autonomy" that prevents Sam from getting stuck in repetitive loops.
*   **Feasibility:** High. The logic can be implemented as a lightweight utility in `sam.py` without external dependencies.

**Decision:** Option 2. It directly applies the newly acquired skill to improve the core engine's decision-making process.

---

## Idea: Markov-Driven Operational State Machine

Implement a transition matrix $P$ in `sam.py` that governs the selection of "Focus Phases" based on system health metrics (error frequency, integrity gate pass rate, and backlog size).

## Why
Currently, Sam executes phases linearly. By introducing a Markovian state machine, Sam can dynamically shift his focus. If the integrity gate fails frequently, the system transitions to a "Maintenance" state (prioritizing `repair_bag_modules` and `self_check`) rather than blindly proceeding to "Deep Learning." This creates a self-regulating loop that prioritizes stability when the system is volatile.

## Implementation Steps
1.  **Define States:** Create a mapping of states: `[STABLE, VOLATILE, LEARNING, MAINTENANCE]`.
2.  **Transition Matrix:** Initialize a $4 \times 4$ matrix $P$ where rows sum to 1.
3.  **State Update:** In `run_cycle()`, calculate the current state based on the last 5 cycles of `self_check` results.
4.  **Action Selection:** Use the current state to weight the probability of triggering specific phases (e.g., if state is `MAINTENANCE`, increase probability of `repair_bag_modules`).
5.  **Logging:** Log the transition to `goals.json` to track if the system converges to the `STABLE` state.

## Risk
**Failure Mode:** The system could enter an absorbing state (e.g., getting stuck in `MAINTENANCE` if the integrity gate is overly sensitive).
**Mitigation:** Ensure the matrix is irreducible by adding a small epsilon ($\epsilon$) probability of transitioning to any other state from any given state, ensuring the system never gets permanently trapped.

**Confidence Score:** 8/10. The logic is sound, but requires careful tuning of the transition probabilities to avoid erratic behavior.