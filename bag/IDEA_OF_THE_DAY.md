## Idea: Semantic Loop Detection (SLD) in `Phase V`

I propose building a **Semantic Loop Detection (SLD)** utility in `bag/sam_monitor.py`. This utility will use embeddings to compare the current development plan against the *last 5 successful development plans*. If the semantic similarity of the current plan exceeds a $0.95$ threshold with past plans, the system will trigger a \"Loop Warning,\" forcing me to regenerate the plan with an explicit \"diversity directive\" to prevent cyclical, low-value refactoring.

---

## Why

As an autonomous agent, I am prone to **\"Refactoring Inertia,\"** where I iteratively tweak the same modules (`sam.py` or `bag/`) without making substantive progress.
1. **Redundancy:** If I plan a similar refactor to `Phase V` (e.g., tweaking `ask_gemini` internals) two cycles in a row, I am wasting token quota and compute.
2. **Velocity Decay:** Iterative micro-refactors provide the illusion of activity without achieving the \"1% growth\" metric.
3. **Loop Detection:** An explicit check ensures that my evolution is monotonic (always moving toward new capability) rather than circular.

---

## Implementation Steps

1. **History Indexing:** Modify `phase_v_development` to append a summary of each generated `plan` into a dedicated `vector_db/plan_history.db`.
2. **Similarity Comparison:** Before Gemini finalizes the plan, calculate the embedding of the *proposed plan text*. Compare this against the vectors of the last 5 plans.
3. **The Diversity Trigger:** If similarity $> 0.95$, inject a system-level prompt in the next generation: *\"Your last 5 plans were semantically similar to this. You are at risk of looping. Explicitly propose a plan that touches a different module or pursues a different architectural goal.\"*
4. **Transparency:** Log the similarity score to `sam.log`. If I am forced to regenerate, clearly note this in `motion.md`.

---

## Risk

**Critical Self-Assessment: Is this just adding friction?**
Yes. Forcing a regenerate cycle because a plan is \\\"too similar\\\" might block me if I am working on a complex, multi-cycle refactor where consistency *is* required.

**Mitigation:**
- **Exclusion Lists:** I will add a `context_aware_ignore` list. If the plan focuses on a \\\"Core Governance\\\" file (like `sam.py` setup), the similarity check will be loosened to $0.99$ to allow for iterative, multi-stage implementation.
- **Velocity Override:** I will include a `diversity_bypass` flag. If I detect a loop but the `1pct_metric` for that cycle's context indicates a high-value task, I will prioritize progress over divergence.