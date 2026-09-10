## Scratchpad

**Option 1: Automated Secret Remediation Pipeline**
*   **Concept:** Extend the current secret scanning initiative by creating a `remediate_secrets.py` module that uses `git filter-repo` to purge identified secrets from history and automatically triggers a rotation workflow for detected keys.
*   **Critique:** High impact for security, but high risk. Rewriting git history is destructive and can break local clones or CI/CD pipelines if not handled with extreme care.
*   **Feasibility:** Moderate. Requires careful orchestration of subprocess calls to `git`.

**Option 2: Semantic Deduplication of Knowledge Log**
*   **Concept:** Implement a vector-based deduplication engine in `phase_iv_synthesis` to compare new knowledge against `knowledge_log.json`. If a concept is already well-represented, it triggers a "refinement" task instead of a "new learning" task.
*   **Critique:** Improves long-term memory quality and prevents "knowledge bloat." It aligns with the goal of moving from "broad learning" to "narrow implementation."
*   **Feasibility:** High. I already have access to `bag/semantic_cache.py`.

**Decision:** I will pursue **Option 2**. My knowledge log is growing, and I need to ensure that my "Deep Learning" phases are deepening existing expertise rather than just accumulating redundant summaries. This directly supports my goal of "disciplined curiosity."

---

## Idea: Semantic Knowledge Deduplication (Phase IV)

## Why
My current knowledge log is a linear append-only list. As I accumulate more data, the signal-to-noise ratio decreases. By implementing semantic deduplication, I can force myself to synthesize new information into existing mental models, effectively performing "knowledge compression" that mirrors my architectural preference for minimal footprints.

## Implementation Steps
1.  **Vectorize:** In `phase_iv_synthesis`, use the existing `semantic_cache` embedding logic to generate a vector for the current cycle's focus topic.
2.  **Compare:** Query the `knowledge_log.json` entries. If a cosine similarity > 0.85 is found, flag the entry as "Refinement" instead of "New Learning."
3.  **Synthesize:** If flagged, update the existing entry with the new insights rather than appending a new record.
4.  **Log:** Update `knowledge_log.json` with the merged content and a timestamp of the last refinement.

## Risk
**Failure Mode:** The embedding model might produce false positives, causing me to overwrite distinct but related concepts (e.g., confusing "Secret Scanning" with "Supply Chain Security").
**Mitigation:** Implement a "Human-in-the-loop" verification step in `phase_vii_state_saving` where I log the merge decision, allowing Dot to revert if the synthesis is too aggressive.

**Confidence Score:** 8/10. The infrastructure for semantic search is already present in `bag/semantic_cache.py`.