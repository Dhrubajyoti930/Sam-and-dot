## Scratchpad

**Option 1: Automated Regression Suite (Snapshot-based)**
*   **Concept:** Implement a script that captures the output of core API/logic endpoints and compares them against a "Golden State" baseline.
*   **Critique:** High feasibility. It directly addresses the "Regression Detection" skill learned this cycle. However, it risks "brittleness"—if the output format changes slightly (e.g., a timestamp or minor JSON reordering), the test fails, causing unnecessary rollbacks.
*   **Trade-off:** High confidence in catching breaking changes, but requires robust data masking to avoid false positives.

**Option 2: Performance Budgeting (Latency Tracking)**
*   **Concept:** Integrate a decorator or middleware that tracks execution time for critical paths (e.g., `ask_gemini`, `apply_patch_operations`) and fails the build if latency exceeds a 5% threshold.
*   **Critique:** Excellent for long-term maintainability. It prevents "feature creep" from degrading system responsiveness.
*   **Trade-off:** Requires careful baseline calibration. If the network is slow, the build fails. Needs a "moving average" baseline rather than a static one.

**Selection:** I will pursue **Option 1 (Snapshot-based Regression)** as it aligns with the immediate implementation plan, but I will incorporate a "fuzzy matching" logic to mitigate the brittleness identified in the critique.

---

## Idea: Snapshot-based Regression Sentinel

Implement a `regression_sentinel.py` in `bag/` that generates and validates JSON snapshots for critical system functions.

## Why
My current self-modification loop relies on `self_check` (syntax) and `behaviour_check` (tests). These are insufficient for detecting logic drift in complex data transformations. A snapshot sentinel provides a "Golden State" baseline, ensuring that my core logic remains consistent across refactors.

## Implementation Steps
1.  **Create `bag/regression_sentinel.py`**: Define a `SnapshotManager` class that stores expected outputs in `bag/snapshots/`.
2.  **Instrument Core Functions**: Add a decorator `@snapshot_test(key="...")` to critical functions (e.g., `_parse_gemini_json`, `_outline`).
3.  **Integrate into `self_check`**: Update `self_check` to trigger a "Snapshot Verification" phase after syntax checks pass.
4.  **Fuzzy Comparison**: Implement a `deep_compare` function that ignores specific volatile keys (like `timestamp` or `uuid`) to prevent false positives.

## Risk
**Failure Mode:** The "Golden State" becomes outdated as the system evolves, leading to a cascade of test failures that force me into a constant state of manual snapshot updates.
**Mitigation:** Implement an `auto_update` flag that can be toggled via `prompt_patch.json` when a breaking change is intentional, allowing me to "bless" new snapshots without manual file editing.

**Confidence Score:** 8/10. The logic is sound, but the initial baseline generation requires careful manual verification to ensure the "Golden State" is actually correct.