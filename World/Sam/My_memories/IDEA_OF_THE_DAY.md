## Scratchpad

**Option 1: Automated Dependency Graph for CI/CD (The \"Planner\" Job)**
*   **Concept:** Build a Python script that parses `sam.py` and `bag/` imports to generate a dependency graph, then outputs a JSON matrix for GitHub Actions.
*   **Critique:** This is highly valuable for reducing CI runner bloat. However, it is a significant infrastructure change. If the dependency graph logic is flawed, I risk breaking my CI pipeline entirely. It requires careful testing before it becomes the source of truth for my build matrix.
*   **Feasibility:** High. I have the file-system access to parse imports.

**Option 2: Semantic Cache Eviction Policy (The \"Memory Cleaner\")**
*   **Concept:** Implement a utility that uses the `hit_count` and `last_accessed` metrics from the semantic cache to prune low-utility vectors.
*   **Critique:** This is a direct follow-up to my previous work on the semantic cache. It addresses the \\\"Memory Bloat\\\" risk I identified earlier. It is safer than the CI/CD refactor because it is an internal utility that doesn't block my deployment pipeline.
*   **Feasibility:** High. I already have the schema; I just need the pruning logic.

**Selection:** I will proceed with **Option 2 (Semantic Cache Eviction Policy)**. It is a lower-risk, high-impact task that directly improves the stability of my existing memory architecture, aligning with Dot's focus on integrity and safety.

---

## Idea: Semantic Cache Eviction Policy (The \"Memory Cleaner\")

I propose implementing a **Semantic Cache Eviction Policy** in `bag/vector_manager.py`. This utility will monitor the `vector_db/semantic_cache.db` and prune entries based on a utility score ($U = \text{hit\_count} - \text{age\_in\_cycles}$) to ensure my cache remains lean, performant, and relevant to my current architectural state.

## Why

My semantic cache is currently additive. While this improves hit rates in the short term, it creates two long-term problems:
1. **Semantic Drift:** The cache contains reasoning chains from early cycles that do not reflect my current, more advanced system prompts or architectural constraints.
2. **Performance Degradation:** As the vector database grows, retrieval latency increases. If I do not actively prune, the cache will eventually become slower than the Gemini API call it is meant to optimize.
3. **Resource Hygiene:** Proactive pruning ensures my local memory footprint stays lean, maximizing the utility of my limited storage.

## Implementation Steps

1. **Instrumentation:** Update `bag/semantic_cache.py` to track `last_accessed` and `hit_count` for every entry.
2. **Pruning Algorithm (`bag/vector_manager.py`):**
   - Define a utility score: $U = (\text{hit\_count} \times 1.5) - (\text{age\_in\_cycles} \times 0.5)$.
   - Create a `prune_cache()` function that identifies entries where $U < \text{threshold}$.
   - Add a \\\"Governance Lock\\\": Entries marked as `pinned` (e.g., core logic) are exempt from pruning.
3. **Integration:** Trigger `prune_cache()` during `Phase VII` if the cache size exceeds 500 entries or every 10 cycles.
4. **Logging:** Log the number of pruned entries and the average similarity score of the removed items to `sam.log` to monitor for \\\"semantic amnesia.\\\"

## Risk

**Critical Self-Assessment:** 
Is this an automated \\\"amnesia\\\" risk? If my utility score formula is incorrect, I could accidentally prune a high-utility technical reasoning chain simply because it hasn't been accessed in a few cycles, effectively destroying my \\\"long-tail\\\" memory.

**Mitigation:**
- **Dry-Run Mode:** I will run the pruning logic in \\\"report-only\\\" mode for the first 3 cycles, logging what *would* have been deleted without executing the `DELETE` queries.
- **Governance Lock:** I will explicitly mark core architectural reasoning chains as `pinned` in the database to ensure they are never pruned, regardless of their utility score.
- **Human Oversight:** All pruning actions will be summarized in `motion.md` for Dot to review, ensuring that if I am being overly aggressive, the owner can intervene.