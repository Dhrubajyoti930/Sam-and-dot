## Scratchpad

**Option 1: Implement a "Semantic Cache" TTL/Eviction Policy.**
*   *Concept:* Currently, the semantic cache is a simple key-value store. Adding an LRU (Least Recently Used) or TTL (Time-To-Live) policy would prevent the cache from growing indefinitely and ensure stale market/technical data is purged.
*   *Critique:* High maintenance. Requires tracking access timestamps and implementing a pruning routine. While "cleaner," it adds complexity to `bag/semantic_cache.py` that might not yield immediate performance gains given the current scale.
*   *Feasibility:* High.

**Option 2: Formalize "Safety Boundaries" for Static Analysis.**
*   *Concept:* Following the learning on Rice’s Theorem, I can define a `safety_boundary.json` that explicitly lists "decidable" code paths (e.g., pure data-processing functions) versus "undecidable" ones (e.g., complex agentic loops). I can then write a custom linter check that warns if I introduce recursion or dynamic memory allocation in the "decidable" zone.
*   *Critique:* This aligns perfectly with my recent learning. It moves from "hoping" for safety to "enforcing" constraints. It is a high-leverage, long-term architectural improvement.
*   *Feasibility:* Medium. Requires careful AST parsing.

**Selection:** Option 2. It directly addresses the "Rice's Theorem" learning and improves the integrity of my self-modification process.

---

## Idea: Formalized Decidability Boundaries

Implement a `SafetyBoundary` validator that uses `ast` to scan for non-decidable constructs (e.g., `while` loops with non-constant conditions, arbitrary recursion) in critical modules, flagging them as "High Risk" during the `self_check()` phase.

## Why
Rice’s Theorem proves I cannot build a perfect analyzer for all behavior. By restricting my own code to a "decidable subset" (e.g., avoiding complex recursion in core logic), I make my code easier to verify and less prone to the "halting" issues that plague autonomous agents.

## Implementation Steps
1.  **Define Constraints:** Create `bag/safety_rules.py` containing a list of AST node types that are "restricted" in core modules (e.g., `ast.While`, `ast.Recursion`).
2.  **Integrate into `self_check()`:** Update `sam.py` to run a `SafetyBoundary` check after the `ruff` check.
3.  **Logging:** If a violation is found, log a warning to `log.info` rather than failing, allowing me to "opt-in" to complexity while being aware of the risk.

## Risk
**Pre-mortem:** The validator might flag necessary, safe code (e.g., a simple `while` loop in a utility function), causing unnecessary friction.
**Mitigation:** Implement an "ignore" mechanism via a specific comment tag (e.g., `# sam: ignore-boundary`) to allow intentional complexity.

## Self-Correction
*Refinement:* Instead of a global ban, I will apply this check *only* to files in `workshop_bench/core/` and `sam.py`. I will start by only checking for `ast.Recursion` to keep the initial implementation focused and low-noise.

**Confidence Score:** 8/10