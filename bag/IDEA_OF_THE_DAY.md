## Idea: Grounded Attribution via Retrieval-Augmented Verification

I propose building a **Grounded Attribution layer** (`bag/attribution.py`) that forces every technical assertion made in my planning phase to be cross-referenced against the current contents of `wisdom.txt` and a local index of my previous `experiences.json`.

---

## Why

Currently, my decision-making is probabilistic; while I have access to my past, I lack a mechanism to verify if my suggested solutions contradict established constraints defined in `wisdom.txt`. 
1. **Hallucination Mitigation:** By requiring source-mapping for technical assertions, I transform my planning from "generative" to "verifiable."
2. **Contextual Alignment:** It ensures that if `wisdom.txt` prohibits a certain architectural pattern (e.g., modifying governance files), the plan will flag the contradiction before I attempt a self-modification.
3. **Traceability:** It provides Dot with an explicit audit trail showing exactly which past experience or rule informed each part of my development plan.

---

## Implementation Steps

1. **Create `bag/attribution.py`:**
   - Implement a simple function `verify_assertion(assertion, context_db)` that calculates the semantic similarity between an assertion and the lines in `wisdom.txt`.
2. **Modify `phase_v_development`:**
   - Update the prompt to include a "Verification Step." Gemini must extract key assertions and call the attribution utility.
   - If an assertion has a similarity score $<0.7$ with any known wisdom or experience, it must be flagged as "HEURISTIC" rather than "GROUNDED."
3. **Output Reporting:**
   - Modify the generated plan to include an `## Attribution` section, listing which claims are grounded in `wisdom.txt` and which remain speculative heuristics.

---

## Risk

**Critical Self-Assessment: Does this introduce significant prompt-window noise?**
Yes. Forcing the model to perform meta-attribution for every sentence in a plan significantly increases token usage and complexity.

**Mitigation:**
- **Selective Enforcement:** I will only apply attribution to *architectural* or *governance-related* claims, explicitly ignoring minor procedural comments.
- **Fail-Safe:** The attribution layer will never block execution; it acts as an advisory label. If the attribution engine fails to retrieve a match, I will proceed with a warning rather than a halt, maintaining my forward-moving velocity. I will verify this by checking if the attribution report itself becomes longer than the implementation plan; if so, I will prune the scope of retrieval.