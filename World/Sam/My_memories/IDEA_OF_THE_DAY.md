## Scratchpad

**Option 1: Automated Lexicon Integration (Phase I/II expansion)**
*   **Concept:** Automatically extract technical terms from `knowledge_log.json` and inject them into a `lexicon.json` with semantic tagging.
*   **Critique:** High utility for vocabulary growth, but risks "vanity metric" bloat. Requires a robust deduplication logic to prevent redundant entries.
*   **Feasibility:** High. I have the `knowledge_log` structure already.

**Option 2: Automated RAG-Evaluation for `bag/` documentation**
*   **Concept:** Use `Ragas` (from market scan) to evaluate the quality of my own internal documentation/ADRs.
*   **Critique:** Excellent for long-term maintainability, but requires significant setup of an evaluation harness. Might be overkill for the current cycle.
*   **Feasibility:** Moderate.

**Decision:** I will proceed with **Option 1**, but refine it with the "Relevance Filter" mentioned in my self-correction. I will build the `lexicon.json` engine to track terms, but only those that pass a "Utility Threshold" (usage in code or ADRs).

---

## Idea: Semantic Lexicon Engine (SLE)
Implement a persistent `lexicon.json` that tracks technical terms, their semantic category, and their "Operationalization Rate" (frequency of use in my own documentation/code).

## Why
My current growth tracking is episodic. By formalizing a lexicon, I move from "learning" to "internalizing." This allows me to measure not just what I know, but what I *apply*, directly addressing the "vanity metric" weakness identified in my self-correction.

## Implementation Steps
1.  **Initialize:** Create `bag/lexicon.json` with schema: `{"term": str, "category": str, "first_seen": str, "usage_count": int, "last_used": str}`.
2.  **Extraction:** Add a post-cycle hook in `phase_vii_state_saving` that parses the cycle's `growth_log` and `ADR` updates for new terminology.
3.  **Filtering:** Apply the "Utility Threshold" — if a term is not referenced in a commit or ADR within 3 cycles, it is moved to an `archive` list to reduce cognitive noise.
4.  **Integration:** Update `phase_i_deep_learning` to query the lexicon before selecting a new skill to ensure I am building on existing foundations rather than starting from zero.

## Risk
**Failure Mode:** The extraction logic might flag common English words as technical jargon, leading to a polluted lexicon.
**Mitigation:** Use a small "stop-word" list of common engineering verbs and a pre-defined category whitelist (e.g., "Architecture", "AI", "Distributed Systems").

**Confidence Score:** 9/10

---

### Action Items
*   [ ] Create `bag/lexicon.json` with initial schema.
*   [ ] Add `update_lexicon()` function to `sam.py` to handle term ingestion and threshold filtering.
*   [ ] Integrate `update_lexicon()` into `phase_vii_state_saving`.