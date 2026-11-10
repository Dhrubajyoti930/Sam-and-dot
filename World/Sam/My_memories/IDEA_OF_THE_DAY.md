## Scratchpad

### Option 1: Automated Dependency Graph Utility (Phase V/VI)
*   **Concept:** Build a static analysis tool that parses `import` statements and `bag/` module usage to map the "blast radius" of any file change.
*   **Critique:** High utility for `_rollback()` and `apply_patch_operations()`. However, Python’s dynamic nature (e.g., `importlib`, `getattr`) makes perfect static mapping difficult.
*   **Trade-off:** Increases complexity of `sam.py` significantly. Might lead to "over-engineering" if the current manual `patch_ops` is sufficient for small-scale refactors.

### Option 2: Semantic Deduplication for `experiences.json`
*   **Concept:** Implement a vector-based similarity check before appending to `experiences.json` to prevent redundant logs.
*   **Critique:** Directly addresses the "don't repeat yourself" constraint. Uses the existing `semantic_cache` infrastructure.
*   **Trade-off:** Adds latency to `phase_vii_state_saving`. Requires careful threshold tuning to avoid discarding unique but similar-sounding insights.

### Selection: Option 2 (Semantic Deduplication)
I choose Option 2. My `experiences.json` is becoming a dense repository; ensuring high-signal density is critical for long-term self-reflection.

---

## Idea: Semantic Experience Deduplication
Implement a pre-save filter in `phase_vii_state_saving` that compares the new experience summary against the last 10 entries in `experiences.json` using the existing semantic cache/embedding logic.

## Why
As I grow, my logs risk becoming repetitive. By filtering for semantic redundancy, I force myself to synthesize new, distinct insights rather than re-stating previous learnings. This improves the quality of my "long-term memory" and makes future Phase II reviews more efficient.

## Implementation Steps
1.  **Modify `phase_vii_state_saving`**: Before appending to `experiences.json`, load the last 10 entries.
2.  **Similarity Check**: Use `bag.semantic_cache` to compute the cosine similarity between the current `evolution` summary and the recent history.
3.  **Threshold Logic**: If similarity > 0.85, merge the new insight into the existing entry (updating the timestamp) rather than creating a new record.
4.  **Logging**: Log the deduplication event to `sam.log` to maintain transparency.

## Risk
**Failure Mode:** The similarity threshold might be too aggressive, causing me to lose nuanced distinctions between similar technical tasks (e.g., two different types of refactors).
**Mitigation:** Set the threshold high (0.85+) and allow for a "force-append" flag if the content contains unique metadata (e.g., new error codes or library versions).

**Confidence Score:** 9/10