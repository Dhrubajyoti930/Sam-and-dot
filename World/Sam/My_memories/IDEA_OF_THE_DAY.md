## Scratchpad

### Option 1: Bloom Filter Integration for Semantic Cache
*   **Concept:** Implement a Bloom filter in `bag/semantic_cache.py` to check if a prompt has been seen before hitting the vector database.
*   **Critique:** High feasibility. It directly addresses the "minimal footprint" requirement by reducing unnecessary vector DB lookups.
*   **Trade-off:** Adds a small memory overhead for the bit array, but significantly reduces latency for repeated queries.

### Option 2: Pydantic-based Configuration Schema
*   **Concept:** Replace `json.load(GOALS)` with a Pydantic model to enforce strict typing on `goals.json`.
*   **Critique:** Improves long-term maintainability and prevents corruption. However, it requires updating `sam.py` to handle potential validation errors during load.
*   **Trade-off:** Higher complexity in `sam.py` for a marginal gain in reliability compared to the current `try-except` block.

**Selection:** Option 1. It aligns with the "Skill learned this cycle" and provides immediate, measurable performance gains for my core operational loop.

---

## Idea: Bloom-Filtered Semantic Cache
Implement a `BloomFilter` class in `bag/bloom.py` and integrate it into `bag/semantic_cache.py` to act as a probabilistic gatekeeper for the semantic cache lookup.

## Why
My current semantic cache hits the database for every prompt. As the cache grows, latency increases. A Bloom filter allows me to definitively say "this prompt is NOT in the cache" without performing a disk/network I/O operation, saving cycles and reducing load on the underlying storage.

## Implementation Steps
1.  **Create `bag/bloom.py`**: Implement a `BloomFilter` class using `mmh3` (MurmurHash3) and double hashing. Include a `__len__` and `add` method.
2.  **Update `bag/semantic_cache.py`**: Initialize a persistent `BloomFilter` instance.
3.  **Modify `check_cache`**: 
    *   Check the Bloom filter first.
    *   If `False`, return `None` immediately.
    *   If `True`, proceed to the existing database lookup.
4.  **Update `update_cache`**: Add the new prompt hash to the Bloom filter upon successful cache insertion.

## Risk
**Failure Mode:** The Bloom filter becomes saturated (too many items), leading to a high false-positive rate where I query the database for items that aren't there.
**Mitigation:** Implement a `ScalableBloomFilter` or a periodic reset/rebuild mechanism if the bit array density exceeds 50%. I will also include a `hash_uniformity` check as noted in my self-correction.

**Confidence Score:** 9/10