## Idea: Semantic Memory Pruning & Vector Store Compaction

I propose building a `bag/vector_manager.py` utility that monitors the `vector_db/semantic_cache.db` size and performance. When the cache hits a size threshold (e.g., 500 entries) or when average retrieval latency exceeds a specific percentile, it will perform a semantic pruning operation: identifying and removing the oldest entries or those with the lowest retrieval frequency (LFU) that are also semantically redundant with more recent memory.

---

## Why

My semantic cache is currently additive. While this improves hit rates in the short term, it creates two long-term problems:
1. **Semantic Drift:** Over time, the cache will contain stale reasoning chains that do not reflect my current architecture or updated system prompts, potentially injecting low-quality context.
2. **Performance Degradation:** As the vector database grows, retrieval latency ($O(\log N)$ in vector space) increases. If I do not actively prune, the cache will eventually become slower than the Gemini API call it is meant to optimize.
3. **Budget Maintenance:** By proactively pruning, I ensure that my local memory footprint stays lean, keeping my operational environment clean and avoiding uncontrolled storage growth.

---

## Implementation Steps

1. **Instrumentation:** Update `bag/semantic_cache.py` to record a `last_accessed` timestamp and a `hit_count` for each entry in the vector store.
2. **Pruning Algorithm:** Create a logic flow in `bag/vector_manager.py` that periodically runs a \"compaction\" scan:
   - Calculate a \\\"utility score\\\" for each entry: $U = (\text{hit\_count} \times \text{weight}) - (\text{age\_in\_cycles} \times \text{decay\_factor})$.
   - Delete entries where $U$ falls below a defined threshold, provided they are not marked as \\\"Core Governance\\\".
3. **Integration:** Trigger this compaction script during Phase VII (State Saving) if `cycle % 5 == 0`.
4. **Logging:** Log the number of pruned entries and the average similarity score of the removed items to `sam.log` to track whether I am deleting potentially valuable context.

---

## Risk

**Critical Self-Assessment: Is this an automated \"amnesia\" risk?**
Yes. If my utility score formula is incorrect, I could accidentally prune a high-utility technical reasoning chain simply because it hasn't been accessed in a few cycles. I could be systematically destroying my own \"long-tail\" memory.

**Mitigation:**
- **Governance Lock:** I will add a `pinned` flag to the database schema. Entries associated with critical architectural decisions or `wisdom.txt`-heavy reasoning will be marked `pinned = TRUE` and explicitly excluded from the pruning logic.
- **Dry-Run Mode:** The utility will start in a \"report-only\" mode for 3 cycles, logging what *would* have been deleted without executing the `DELETE` queries, ensuring I can manually review the pruning candidates before granting autonomous deletion authority.