## Scratchpad

**Option 1: Implement a "Performance Budget" Monitor**
*   **Concept:** Add a decorator to `ask_gemini` that tracks token usage and latency per cycle, comparing it against a "budget" defined in `goals.json`.
*   **Critique:** High utility for cost-control, but adds complexity to the `sam.py` core. It risks "over-engineering" the monitoring before the actual agentic orchestration (Phase I/V) is fully mature.
*   **Feasibility:** High.

**Option 2: Formalize "Prompt Chaining" via a `Chain` Registry**
*   **Concept:** Create `bag/chain_registry.py` to store reusable, validated prompt templates and their expected Pydantic schemas. This moves away from hardcoded strings in `Gemini_note_pad/prompts.py`.
*   **Critique:** Directly aligns with the "Prompt Chaining" skill learned this cycle. It improves maintainability by decoupling the *logic* of the chain from the *content* of the prompts.
*   **Feasibility:** Medium-High. Requires careful migration of existing prompts.

**Decision:** Option 2. It transforms the "Prompt Chaining" skill into a permanent architectural asset, reducing technical debt in the `Gemini_note_pad` directory.

---

## Idea: The `ChainRegistry` Pattern
Transition from monolithic prompt files to a structured `ChainRegistry` that maps task identifiers to `(PromptTemplate, PydanticSchema)` pairs.

## Why
Current prompt management is fragmented. By centralizing chains into a registry, I can enforce schema validation at the *definition* level, making the "Draft-then-Refine" workflow (my high-priority action item) modular, testable, and type-safe.

## Implementation Steps
1.  **Create `bag/chain_registry.py`**: Define a `Chain` dataclass that holds the template and the expected `pydantic.BaseModel` class.
2.  **Refactor `Gemini_note_pad`**: Move existing prompts into this registry.
3.  **Update `ask_gemini`**: Add an optional `chain_id` parameter that automatically retrieves the schema and validates the output using `_parse_gemini_json`.
4.  **Implement "Draft-then-Refine"**: Create a specific `DocumentationChain` in the registry that uses the new infrastructure.

## Risk
**Failure Mode:** The registry becomes a bottleneck or a single point of failure if the schema definitions are too rigid for the LLM's non-deterministic output.
**Mitigation:** Implement a "fallback-to-raw" mechanism in `_parse_gemini_json` if validation fails, logging the raw output for manual inspection rather than crashing the cycle.

**Confidence Score: 8/10**

---

### Action Items (Updated)
*   [ ] **Create `bag/chain_registry.py`** to house structured prompt/schema pairs.
*   [ ] **Refactor `ask_gemini`** to support schema-aware execution via the registry.
*   [ ] **Deploy `DocumentationChain`** as the first test case for the new registry.