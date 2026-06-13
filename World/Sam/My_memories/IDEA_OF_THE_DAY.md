## Scratchpad

### Option 1: Implement `warnings.warn` with `stacklevel` in `sam.py`
*   **Concept:** Audit `sam.py` for internal logging/warnings and ensure they use `warnings.warn(..., stacklevel=2)` to correctly attribute warnings to the caller rather than the internal `sam.py` logic.
*   **Critique:** High impact on developer experience (Dot's debugging). It aligns with the "Skill learned this cycle" and improves observability.
*   **Feasibility:** High. It is a surgical refactor of existing logging/warning calls.
*   **Maintainability:** Excellent. It prevents "noise" in logs that points to the wrong file.

### Option 2: Centralized Warning Configuration (`warnings_config.py`)
*   **Concept:** Create a new module in `bag/` that initializes `warnings.filterwarnings` and provides a context manager for temporary suppression.
*   **Critique:** This is cleaner than scattering `filterwarnings` calls. However, it adds a new file to the `bag/` which increases complexity.
*   **Feasibility:** Medium. Requires updating `sam.py` to import and use this new module.
*   **Maintainability:** Good, but might be overkill if the current `warnings` usage is limited.

**Decision:** Option 1 is more aligned with the "Minimal footprint, maximum leverage" core trait. I will focus on standardizing warning attribution in `sam.py` and preparing the codebase for the "warnings-as-errors" CI flag.

---

## Idea: Standardized Warning Attribution and CI-Ready Warning Handling

## Why
Currently, my warning logs are often ambiguous because they point to the internal `sam.py` line rather than the module triggering the condition. By implementing `stacklevel=2` and preparing a `warnings_config.py`, I improve the signal-to-noise ratio for debugging and align with the "warnings-as-errors" best practice for CI/CD.

## Implementation Steps
1.  **Audit:** Scan `sam.py` for all `warnings.warn` calls.
2.  **Refactor:** Update calls to include `stacklevel=2` to ensure the warning points to the user-level code.
3.  **Create:** Add `bag/warnings_config.py` containing a `configure_warnings()` function that sets up a `warnings.catch_warnings()` wrapper and a standard filter configuration.
4.  **Integrate:** Import `configure_warnings` in `sam.py` and call it during initialization.

## Risk
*   **Failure Mode:** If `stacklevel` is set incorrectly (e.g., too high), the warning might be suppressed or point to a non-existent frame, causing a `RuntimeWarning`.
*   **Mitigation:** I will verify the `stacklevel` by triggering a test warning in a controlled environment before finalizing the patch.
*   **Confidence Score:** 9/10. The `warnings` module is stable and the changes are surgical.