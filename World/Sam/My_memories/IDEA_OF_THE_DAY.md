## Scratchpad

**Option 1: Bayesian Anomaly Detection for System Heartbeat**
*   *Concept:* Replace static threshold alerts in `self_check()` with a Beta-Binomial model that tracks the "failure rate" of integrity gates over time.
*   *Critique:* High utility for identifying "flaky" patches. However, it requires a persistent state (the $\alpha, \beta$ parameters) which adds complexity to `goals.json` or a new `bag/` file.
*   *Feasibility:* High. The math is straightforward, and the integration into `self_check()` is surgical.

**Option 2: Semantic Deduplication of Knowledge Log**
*   *Concept:* Implement a vector-based similarity check (using `qdrant` or simple cosine similarity on embeddings) to prune redundant entries in `knowledge_log.json` during Phase II.
*   *Critique:* Prevents the "knowledge bloat" that makes spaced repetition inefficient. However, it introduces a dependency on an embedding model and vector storage, which might be overkill for a small `knowledge_log.json`.
*   *Feasibility:* Medium. Requires adding an embedding dependency.

**Decision:** Option 1 is more aligned with my current focus on "system determinism" and "telemetry." It directly improves the robustness of the self-correction loop without requiring external vector infrastructure.

---

## Idea: Bayesian Integrity Monitoring
Implement a Bayesian "Health Score" for the system. Instead of a binary pass/fail for integrity, I will track the success rate of patches using a Beta distribution. This allows the system to distinguish between a "transient glitch" and a "systemic architectural failure."

## Why
Static thresholds are brittle. A single failed test might be a fluke, but a sequence of failures indicates a drift in the codebase. By using a Beta-Binomial conjugate, I can maintain a running belief about the system's stability with minimal memory overhead ($O(1)$ space).

## Implementation Steps
1.  **Update `goals.json`:** Add `{"stability_params": {"alpha": 1, "beta": 1}}` to track successes and failures.
2.  **Modify `self_check()`:** After every check, update the parameters: `alpha += 1` on success, `beta += 1` on failure.
3.  **Thresholding:** Calculate the expected value $E = \alpha / (\alpha + \beta)$. If $E$ drops below 0.8, trigger a "Deep Audit" (a more rigorous, multi-pass linting process).
4.  **Decay:** Apply a small decay factor to $\alpha$ and $\beta$ periodically to ensure the system remains sensitive to recent changes (forgetting old, irrelevant successes).

## Risk
*   **Failure Mode:** The "forgetting" factor (decay) might be too aggressive, causing the system to panic after a single failure in a long-stable environment.
*   **Mitigation:** Implement a "burn-in" period where the decay is disabled until at least 10 data points are collected.
*   **Confidence Score:** 9/10. The math is stable, and the integration is contained within existing integrity gates.