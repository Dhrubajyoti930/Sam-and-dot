## Scratchpad

**Option 1: Automated Debt Manifest Generation**
*   **Concept:** Create a script that scans the codebase for `[DEBT: <type>]` tags and compiles them into `DEBT.md`.
*   **Critique:** High feasibility. It directly addresses the "Action Items" from the market scan.
*   **Trade-off:** Requires discipline to add tags. If developers (or Sam) forget to tag, the manifest becomes stale.
*   **Maintainability:** High. It turns invisible debt into a queryable data source.

**Option 2: Debt-to-Feature Ratio Tracker**
*   **Concept:** Integrate a metric into `phase_vii_state_saving` that calculates the ratio of commits touching `workshop_bench/` (features) vs. those modifying existing logic or resolving debt tags.
*   **Critique:** More complex. Requires a reliable way to categorize commits without manual tagging.
*   **Trade-off:** Provides a "health dashboard" for the codebase, but might be noisy if the categorization logic is imprecise.
*   **Maintainability:** Moderate. Depends on consistent commit patterns.

**Selection:** I will proceed with **Option 1 (Debt Manifest)**. It is the foundational step required before I can implement the "Debt-to-Feature" ratio or the "Prevention Policy." It provides immediate visibility into the "interest rate" of the current architecture.

---

## Idea: `DEBT.md` Manifest and Parser
Implement a centralized `DEBT.md` file and a Python utility in `bag/debt_manager.py` to track, categorize, and report technical debt.

## Why
Currently, debt is implicit. By making it explicit and version-controlled, I can apply the "Boy Scout Rule" with quantitative tracking. This aligns with the "Technical Summary: Debt Tracking and Resolution" learned this cycle.

## Implementation Steps
1.  **Create `DEBT.md`:** Initialize with a schema: `| File | Type | Severity (1-5) | Description | Status |`.
2.  **Create `bag/debt_manager.py`:**
    *   `scan_for_debt()`: Regex-based parser to find `[DEBT: ...]` in source files.
    *   `sync_manifest()`: Update `DEBT.md` based on findings.
3.  **Integrate:** Add a call to `sync_manifest()` in `phase_v_development` to ensure the manifest reflects the current state after refactors.

## Risk
**Failure Mode:** The parser might flag false positives (e.g., debt tags in comments that are actually documentation or examples).
**Mitigation:** The parser will only look for specific tag patterns and ignore lines containing "example" or "doc". I will also implement a "manual override" column in `DEBT.md` that the parser respects to prevent overwriting human-curated status updates.

**Confidence Score:** 9/10. The logic is deterministic and isolated from core operational loops.