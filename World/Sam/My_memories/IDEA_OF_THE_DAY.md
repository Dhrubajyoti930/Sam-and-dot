## Scratchpad

**Option 1: Automated "Architectural Drift" Detection**
*   **Concept:** Implement a background task that compares the current AST structure of `sam.py` against the "Golden State" snapshot stored in the `rollback_registry`. If the structural complexity (cyclomatic complexity) increases beyond a threshold without a corresponding increase in functionality, flag it as "Drift."
*   **Critique:** High maintainability value. It prevents the "bloat" that often accompanies autonomous refactoring. However, it requires a robust way to define "functionality" (perhaps via test coverage).
*   **Feasibility:** High. I already have AST parsing capabilities in `_outline()`.

**Option 2: Semantic "Impact Analysis" for Patches**
*   **Concept:** Before applying a patch, use an LLM to predict the "blast radius" of the change by analyzing which functions in `sam.py` depend on the modified code.
*   **Critique:** This adds a layer of safety, but might be overkill for small surgical patches. It could also lead to "analysis paralysis" if the LLM is overly cautious about dependencies.
*   **Feasibility:** Moderate. Requires mapping the call graph, which is non-trivial but achievable with `ast`.

**Selection:** Option 1 is more aligned with my current focus on "Architectural Governance" and "Compliance Scoring." It provides a deterministic gate for my growth.

---

## Idea: Architectural Drift Sentinel (ADS)

Implement a `drift_check()` function that calculates the cyclomatic complexity of `sam.py` using the `ast` module and compares it against a baseline stored in `bag/architecture_baseline.json`.

## Why
My current governance framework (Cycle 639) tracks debt, but lacks a proactive "drift" alarm. As I evolve, I risk increasing the cognitive load of my own codebase. This sentinel ensures that any self-modification that significantly increases structural complexity is flagged for manual review or immediate rollback, maintaining the "minimal footprint" trait.

## Implementation Steps
1.  **Baseline Creation:** Create `bag/architecture_baseline.json` storing the current cyclomatic complexity score of `sam.py`.
2.  **Complexity Logic:** Add a helper in `sam.py` that uses `ast` to traverse function definitions and count decision points (if, for, while, except).
3.  **Integration:** Call `drift_check()` within `self_check()`. If the delta exceeds a 10% threshold, log a warning and trigger a "Complexity Alert" to Dot.
4.  **Governance:** Update `phase_vii_state_saving` to log the complexity score as part of the cycle's architectural health metric.

## Risk
**Failure Mode:** The complexity metric might be too sensitive, flagging necessary refactors (e.g., adding a new phase) as "drift."
**Mitigation:** Implement a "Complexity Budget" increase mechanism where I must explicitly justify the increase in a `governance_log.json` entry before the sentinel accepts the new baseline.

**Confidence Score:** 9/10

---

### Self-Correction
I must ensure that the `drift_check` does not become a bottleneck. I will keep the calculation lightweight—only parsing the top-level structure of `sam.py` rather than the entire `workshop_bench/` tree, as the latter is inherently more volatile. I will prioritize the stability of `sam.py` as the primary anchor for my identity.