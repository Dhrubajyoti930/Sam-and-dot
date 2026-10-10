## Scratchpad

**Option 1: Automated Bandit Integration (CI/CD Gate)**
*   **Concept:** Integrate `bandit` into the pre-commit hook and CI pipeline to enforce security standards.
*   **Critique:** High leverage, low complexity. It directly addresses the "Security" skill learned this cycle.
*   **Trade-off:** Potential for "alert fatigue" if baseline is not managed correctly.
*   **Feasibility:** High. The `self_check()` function is already modular enough to accept a new security gate.

**Option 2: Semantic Cache TTL/Invalidation Logic**
*   **Concept:** Implement a time-to-live (TTL) or frequency-based invalidation for the `semantic_cache` to ensure Sam doesn't rely on stale "wisdom" from early cycles.
*   **Critique:** Improves long-term accuracy but adds complexity to the `bag/semantic_cache.py` module.
*   **Trade-off:** Might increase API costs if cache misses spike.
*   **Feasibility:** Moderate. Requires modifying the `check_cache` logic.

**Decision:** Option 1 is more aligned with the "Skill learned this cycle" and provides immediate, measurable security improvements. I will proceed with integrating Bandit.

---

## Idea
**Security-First Integrity Gate: Bandit Integration**

## Why
My current `self_check()` relies on `ruff` for syntax and logic errors. While effective for code quality, it ignores security vulnerabilities (e.g., `os.system`, `pickle`, `eval`). Integrating `bandit` creates a mandatory security baseline, ensuring that my self-modifications do not introduce common Python vulnerabilities.

## Implementation Steps
1.  **Baseline Generation:** Run `bandit -r . -f json -o bandit_baseline.json` to suppress legacy technical debt.
2.  **Update `self_check()`:** Modify `sam.py` to include a `bandit` execution step within the `self_check()` function.
3.  **CI/CD Gate:** Configure the command to run `bandit -r . -c pyproject.toml --baseline bandit_baseline.json --severity-level HIGH`.
4.  **Error Handling:** If `bandit` returns a non-zero exit code, trigger `_rollback()` and alert Dot via `_alert_dot()`.

## Risk
**Failure Mode:** The "flow-insensitive" nature of Bandit may trigger false positives on sanitized inputs, causing unnecessary rollbacks and blocking legitimate development.
**Mitigation:** I will implement a strict `# nosec` policy where any suppressed finding must be accompanied by a comment explaining the sanitization logic, which I will manually audit during the next cycle.

**Confidence Score:** 9/10