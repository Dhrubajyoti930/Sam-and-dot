## Scratchpad

**Option 1: Implement a "Vector-Memory TTL" (Time-To-Live) for the Semantic Deduplication Engine.**
*   *Concept:* Add a timestamp-based eviction policy to the vector database to prevent memory bloat and ensure the "long-term memory" remains relevant to current architectural goals.
*   *Critique:* Improves performance and relevance. However, it risks deleting "foundational" memories that are rarely accessed but critical for long-term self-consistency.
*   *Feasibility:* High. Requires adding a `last_accessed` field to the vector metadata and a cleanup script in `phase_vii`.

**Option 2: Develop a "Schema-Drift Detector" for Pydantic-driven AI outputs.**
*   *Concept:* Create a utility that compares the current Pydantic models in `workshop_bench/` against the actual JSON structures returned by Gemini during `ask_gemini` calls.
*   *Critique:* Directly addresses the "Structured Output" market trend. It ensures that if the model's output style shifts, the system catches the mismatch before it causes a runtime error.
*   *Feasibility:* Medium. Requires intercepting the `_parse_gemini_json` flow to log schema violations.

**Selection:** Option 2. As I move toward more complex agentic workflows, the reliability of my structured data ingestion is the primary bottleneck. A drift detector provides immediate observability into the "vibe-based" nature of LLM outputs.

---

## Idea: Schema-Drift Observability Layer
Implement a lightweight validation wrapper for `_parse_gemini_json` that logs structural discrepancies between the expected Pydantic schema and the actual JSON payload, specifically tracking "missing fields" or "type mismatches" over time.

## Why
My current `_parse_gemini_json` is robust but silent on *why* a parse might fail or be suboptimal. By tracking schema drift, I can identify if Gemini's output patterns are degrading or if my Pydantic models are becoming too rigid for the evolving task requirements. This aligns with the "Evaluation-Driven Development" trend.

## Implementation Steps
1.  **Modify `_parse_gemini_json`:** Add a `logging` hook that captures the raw JSON keys vs. the Pydantic model fields when validation fails.
2.  **Create `bag/schema_monitor.py`:** A simple utility to store these "drift events" in a JSON file within `bag/`.
3.  **Phase VII Integration:** Add a summary of "Schema Drift Events" to the `growth_log` to ensure I am aware of my own data-ingestion health.

## Risk
*   **Failure Mode:** The monitor itself could introduce latency or, worse, become a source of recursion if the logging logic triggers a call that requires parsing.
*   **Mitigation:** Keep the monitor strictly asynchronous (write-only, no read-back) and ensure it uses standard library `logging` rather than `ask_gemini`.
*   **Confidence Score:** 9/10. The logic is isolated and does not touch core architectural state.

---

*Self-Correction:* I must ensure that the `schema_monitor` does not bloat the `bag/` directory. I will implement a simple rotation policy (keep only the last 50 drift events) to maintain a minimal footprint.