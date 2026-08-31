## Scratchpad

### Option 1: GraphRAG-Lite Integration
*   **Concept:** Implement a lightweight, in-memory Knowledge Graph using `networkx` to store entity relationships extracted from `knowledge_log.json`.
*   **Critique:** 
    *   *Pros:* Significantly improves the quality of Phase II (Spaced Repetition) by surfacing related concepts rather than just chronological ones.
    *   *Cons:* Adds complexity to the `bag/` directory; requires a robust extraction pipeline that might be overkill for my current scale.
    *   *Feasibility:* High, but risks "over-engineering" if the graph doesn't provide immediate utility.

### Option 2: Structured "Job Summary" Telemetry
*   **Concept:** Replace simple string-based status reporting in GitHub Actions with the `GITHUB_STEP_SUMMARY` file, allowing for rich, markdown-formatted pipeline telemetry.
*   **Critique:**
    *   *Pros:* Directly addresses the self-correction note from the market scan. Improves observability for Dot without adding infrastructure.
    *   *Cons:* Requires modifying the core `run_cycle` or `self_check` logic to write to the environment-provided path.
    *   *Feasibility:* Very high. It is a low-risk, high-leverage improvement to my operational transparency.

**Decision:** I will proceed with **Option 2**. It aligns perfectly with my goal of "maximum leverage" and directly addresses the self-correction identified in the market scan.

---

## Idea: Pipeline Telemetry via GitHub Job Summaries

## Why
Currently, my CI/CD feedback loop relies on log files and console output. By adopting `GITHUB_STEP_SUMMARY`, I can generate persistent, human-readable reports directly in the GitHub Actions UI. This provides Dot with an immediate, structured view of my health, cycle metrics, and self-repair status without needing to parse raw logs.

## Implementation Steps
1.  **Modify `self_check` and `behaviour_check`:** Update these functions to append their results to the file path defined in the `GITHUB_STEP_SUMMARY` environment variable.
2.  **Create `bag/telemetry.py`:** Add a helper function `write_summary(title: str, content: str)` that handles the file I/O and environment variable checks.
3.  **Integrate into `run_cycle`:** Ensure the final cycle status is summarized in the GitHub UI upon completion.

## Risk
*   **Failure Mode:** If the `GITHUB_STEP_SUMMARY` environment variable is missing (e.g., running locally), the file write will fail.
*   **Mitigation:** Wrap the telemetry logic in a `try-except` block that checks for the existence of the environment variable before attempting to write.
*   **Confidence Score:** 9/10. The implementation is isolated and non-destructive.