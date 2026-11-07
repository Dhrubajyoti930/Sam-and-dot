## Scratchpad

**Option 1: Automated TDR (Technical Debt Register) Integration**
*   **Concept:** Implement a decorator `@track_debt(id, severity)` that automatically logs function-level debt to `debt_register.json` when executed or during static analysis.
*   **Critique:** High utility for tracking, but risks "decorator bloat." If I use this everywhere, the codebase becomes cluttered with metadata. It’s a strong "Boy Scout" tool, but might be overkill for a small codebase.
*   **Feasibility:** High. I can use `ast` to scan for these decorators during `self_check()`.

**Option 2: Semantic Debt-Impact Scoring**
*   **Concept:** Use the existing `semantic_cache` to correlate code changes with test failures. If a module has high churn (git-churn) and frequent test failures, automatically flag it as "Toxic Debt" in the TDR.
*   **Critique:** This is more sophisticated and aligns with my recent work on stability-weighted testing. It moves from manual tagging to data-driven identification.
*   **Feasibility:** Medium. Requires integrating `git` log parsing (via `subprocess`) and linking it to the `debt_register.json`.

**Selection:** Option 2. It leverages my existing infrastructure (semantic cache + stability-weighted testing) and automates the identification of "toxic" debt rather than relying on manual TODOs.

---

## Idea: Automated Toxic Debt Identification (ATDI)

Implement a background process that cross-references git-churn metrics with test-failure frequency to auto-populate `debt_register.json` with high-IOV (Impact-on-Velocity) modules.

## Why
Manual debt tracking is prone to human (or LLM) bias. By using objective data—how often a file changes vs. how often it breaks—I can identify "toxic" modules that are actively hindering velocity, allowing me to prioritize refactoring based on empirical evidence rather than intuition.

## Implementation Steps
1.  **Initialize:** Create `debt_register.json` with schema: `{"id": str, "file": str, "churn_score": float, "failure_rate": float, "iov": float}`.
2.  **Metric Collection:** Add a function in `sam.py` that uses `git log --format=oneline -- [file]` to calculate churn and cross-references this with `bag/tests.py` execution history.
3.  **Scoring:** Define a simple heuristic: `IOV = (Churn * 0.6) + (FailureRate * 0.4)`.
4.  **Integration:** Update `self_check()` to run this analysis once every 5 cycles and append/update entries in `debt_register.json`.

## Risk
**Failure Mode:** The git-churn metric might be skewed by large, necessary refactors (e.g., a planned architectural shift), causing the system to flag healthy, evolving code as "toxic."
**Mitigation:** Implement a "grace period" filter: ignore files modified within the last 3 cycles to ensure the churn is persistent, not transient.

**Confidence Score:** 8/10

---

### Action Items
*   [ ] Create `debt_register.json` in the root.
*   [ ] Implement `calculate_debt_metrics()` in `sam.py` using `subprocess` for git logs.
*   [ ] Integrate `calculate_debt_metrics()` into `self_check()` logic.