## Scratchpad

**Option 1: Agentic Orchestration (Multi-Agent Frameworks)**
*   **Concept:** Integrate a multi-agent orchestration layer to handle complex tasks (e.g., separating "Researcher," "Coder," and "Reviewer" agents).
*   **Critique:** High complexity. Introducing a framework like CrewAI adds significant dependency weight and potential for non-deterministic behavior. While powerful, it might be overkill for my current internal maintenance tasks.
*   **Feasibility:** Moderate. Requires significant refactoring of `ask_gemini` to support multi-turn, multi-agent state management.

**Option 2: Structured Output Enforcement (Instructor/Pydantic)**
*   **Concept:** Replace manual JSON parsing in `_parse_gemini_json` with a robust schema-enforcement layer using `instructor` or native Pydantic integration.
*   **Critique:** High impact, low footprint. This directly addresses the "schema engineering" trend. It improves the reliability of my self-modification patches and goal-tracking. It is highly maintainable and aligns with my goal of reducing "vibes-based" parsing.
*   **Feasibility:** High. I already use Pydantic in `_parse_gemini_json`. Expanding this to enforce schemas on *all* Gemini interactions (not just JSON) is a natural evolution.

**Decision:** Option 2. It provides the highest leverage for my current architecture by hardening the interface between my logic and Gemini's output.

---

## Idea
**Hardened Schema-Driven Interaction Layer**

## Why
My current `_parse_gemini_json` is a reactive utility. By moving to a proactive schema-enforcement model, I can guarantee that every interaction with Gemini—whether for code patches, market analysis, or goal updates—adheres to a strict Pydantic contract before the data ever touches my internal state. This eliminates the "fragile parsing" failure mode entirely.

## Implementation Steps
1.  **Define Core Schemas:** Create `bag/schemas.py` containing Pydantic models for `PatchOperation`, `MarketTrend`, and `GoalUpdate`.
2.  **Refactor `ask_gemini`:** Update the function to accept an optional `response_model` parameter.
3.  **Integrate Enforcement:** Use the `response_model` to validate the output immediately upon receipt. If validation fails, trigger a single, structured retry with the Pydantic error message fed back to Gemini.
4.  **Update `apply_self_modification`:** Transition from raw JSON parsing to using the `PatchOperation` schema to ensure all patches are valid before they reach `apply_patch_operations`.

## Risk
**Failure Mode:** Gemini may struggle to adhere to complex nested schemas in a single pass, leading to repeated validation failures and wasted tokens.
**Mitigation:** Implement a "Schema-First" prompt strategy where the Pydantic model is serialized into the system prompt, providing the model with a clear structural template.
**Confidence Score:** 9/10. The logic is sound, and the dependency (Pydantic) is already present in my environment.