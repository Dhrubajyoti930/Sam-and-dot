## Scratchpad

**Option 1: Implement a `traceback` Sanitizer for Logs.**
*   *Concept:* Create a utility that filters internal project paths from stack traces before they hit the logs, as identified in the "Skill learned" section.
*   *Critique:* High feasibility. It directly addresses the "Action Items" from the skill learning. It improves log signal-to-noise ratio.
*   *Trade-off:* Requires modifying the logging pipeline, which is sensitive.

**Option 2: Async ExceptionGroup Handling.**
*   *Concept:* Refactor `_behaviour_check` or other async-heavy routines to explicitly handle `ExceptionGroup` using the new `traceback` knowledge.
*   *Critique:* Higher complexity. It addresses a modern Python best practice but might be overkill if the current `subprocess` calls don't trigger complex nested exceptions.
*   *Trade-off:* Increases robustness but adds code surface area.

**Decision:** Option 1 is more aligned with my current need for "Minimal footprint, maximum leverage." It cleans up the observability layer without introducing new architectural complexity.

---

## Idea: `Traceback` Sanitizer for Production Logs

Implement a `sanitize_traceback` utility in `bag/utils.py` that uses `traceback.StackSummary` to strip internal file paths and sensitive local context from stack traces before they are passed to the logger.

## Why
My logs currently contain full absolute paths to my `workshop_bench/` and `bag/` directories. This is noisy and exposes internal structure. By filtering these, I improve log readability and focus on the actual exception logic, adhering to the "Minimal footprint" principle.

## Implementation Steps
1.  Create `bag/log_utils.py` with a function `format_sanitized_exception(exc_info)`.
2.  Use `traceback.extract_tb(exc_info[2])` to get a `StackSummary`.
3.  Iterate through the `FrameSummary` objects, replacing the `filename` attribute with a relative path or a generic placeholder if it matches `SAM_DIR`.
4.  Use `traceback.StackSummary.from_list()` to reconstruct the summary.
5.  Update `sam.py`'s `_rollback` and `_behaviour_check` to use this new formatter instead of raw `traceback` output.

## Risk
**Failure Mode:** The sanitizer might accidentally strip useful debugging information if the path-matching logic is too aggressive (e.g., stripping standard library paths).
**Mitigation:** Implement a strict whitelist/blacklist approach: only sanitize paths that start with `SAM_DIR`.
**Confidence Score:** 9/10