## Scratchpad

**Option 1: Semantic Deduplication of Knowledge Logs (Phase IV)**
*   **Concept:** Implement a vector-based similarity check for `knowledge_log.json` to merge redundant entries or identify overlapping concepts before they reach the Spaced Repetition engine.
*   **Critique:** High value for long-term memory efficiency. However, it requires integrating a local embedding model (e.g., `sentence-transformers`) or an API call to generate embeddings, which increases complexity and latency.
*   **Feasibility:** Moderate. I have the infrastructure to store JSON, but the embedding pipeline adds a new dependency.

**Option 2: Automated "Drift Detection" for `sam.py` (Phase V)**
*   **Concept:** Create a background task that compares the current `sam.py` against the `rollback_registry` snapshots to detect "silent" structural drift—changes that pass syntax checks but deviate from the established architectural patterns.
*   **Critique:** Excellent for long-term maintainability. It forces me to confront whether my self-modifications are actually converging toward the desired architecture or just "patching over" issues.
*   **Feasibility:** High. I already have the snapshots; I just need a script to perform a structural diff (AST-based) rather than a line-by-line diff.

**Selection:** Option 2. It aligns with my core trait of "disciplined curiosity" and ensures that my self-improvement doesn't lead to architectural entropy.

---

## Idea: Structural Drift Detection (The "Architectural Compass")

Implement a `detect_drift()` function that performs an AST-based comparison between the current `sam.py` and the most recent healthy snapshot in `rollback_registry`.

## Why
As I continue to apply surgical patches, the risk of "architectural drift"—where the code structure becomes increasingly fragmented or deviates from the original design intent—increases. A simple syntax check (`ruff`) is insufficient to catch structural degradation. By comparing AST nodes, I can identify if I am adding too many helper functions, bloating existing ones, or violating the established module boundaries.

## Implementation Steps
1.  **AST Extraction:** Use `ast.parse()` to extract a list of function/class signatures and their line counts from `sam.py`.
2.  **Snapshot Comparison:** Load the latest `sam_*.py` from `rollback_registry`, parse it, and compare the node signatures against the current state.
3.  **Drift Report:** If the number of functions has increased by >10% or if core functions (e.g., `ask_gemini`) have grown significantly in complexity (line count), log a `WARN` level alert to `goals.json`.
4.  **Integration:** Add `detect_drift()` to the `self_check()` routine so that every cycle includes an architectural health check.

## Risk
**Failure Mode:** The AST comparison might flag legitimate, necessary refactors as "drift," leading to false positives that clutter the logs and trigger unnecessary alerts.
**Mitigation:** Implement a "drift threshold" (e.g., ignore changes in `bag/` modules, focus only on `sam.py` core logic) and allow for a "drift baseline" update if the structural change is intentional and approved by a successful `behaviour_check`.

**Confidence Score:** 8/10