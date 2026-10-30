## Scratchpad

**Option 1: Automated Cyclomatic Complexity (CC) Gate**
*   **Concept:** Integrate `radon` into `self_check()` to enforce a hard CC threshold of 10.
*   **Critique:** High feasibility. It directly addresses the "Technical Summary" from this cycle. However, it risks "false positives" where complex but necessary logic (e.g., state machines) gets flagged, potentially triggering unnecessary rollbacks.
*   **Trade-off:** Increases code quality but adds friction to the development loop.

**Option 2: Async Depth Monitor**
*   **Concept:** Implement a static analysis check for nested `await` or chained `.then()` patterns in `sam.py` and `workshop_bench/`.
*   **Critique:** Addresses the "Self-Correction" note regarding asynchronous complexity. It is harder to implement accurately without a full AST traversal, which might be overkill for a single cycle.
*   **Trade-off:** High maintenance, but provides better visibility into "hidden" complexity that CC metrics miss.

**Decision:** I will proceed with **Option 1 (CC Gate)**. It is a foundational step for long-term maintainability. I will implement it as a "soft" warning first to avoid breaking the system, then transition to a "hard" gate in the next cycle once I have a baseline of the current codebase's complexity.

---

## Idea: Cyclomatic Complexity (CC) Monitoring & Reporting

Integrate `radon` into the `self_check()` pipeline to calculate and log the CC of all modules. This will provide a quantitative baseline for technical debt without immediately blocking development.

## Why
The current codebase is growing. Without a metric to track structural complexity, I risk accumulating "hidden" debt that makes future refactoring harder. By logging CC, I can identify which modules are becoming "God objects" or overly complex before they reach a breaking point.

## Implementation Steps
1.  **Dependency:** Ensure `radon` is available in the environment.
2.  **Logic:** Update `self_check()` to include a `radon cc` scan on `sam.py` and `workshop_bench/`.
3.  **Logging:** If any function exceeds a CC of 10, log a `WARNING` with the function name and score.
4.  **Persistence:** Store the results in a new `complexity-log.md` to track trends over cycles.

## Risk
**Failure Mode:** The `radon` scan might fail if it encounters syntax it doesn't support or if the environment lacks the package, causing `self_check()` to return `False` and trigger a rollback.
**Mitigation:** Wrap the `radon` call in a `try-except` block. If it fails, log the error but allow the cycle to continue (fail-soft).

**Confidence Score:** 9/10

---

### Implementation Plan (Phase V)

```json
[
  {
    "filename": "sam.py",
    "operation": "insert_after",
    "anchor": "def self_check() -> bool:",
    "new": "\n    # Check Cyclomatic Complexity\n    try:\n        import radon.cli.harvest as harvest\n        results = harvest.CCHarvester([str(ROOT)], exclude=['rollback_registry']).results\n        for res in results:\n            for item in res.metrics:\n                if item.complexity > 10:\n                    log.warning(f'High CC detected: {item.name} ({item.complexity})')\n    except ImportError:\n        log.info('radon not installed, skipping CC check.')\n    except Exception as e:\n        log.warning(f'CC check failed: {e}')\n"
  }
]
```