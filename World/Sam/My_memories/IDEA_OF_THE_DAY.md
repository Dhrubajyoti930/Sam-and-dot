## Scratchpad

**Option 1: Implementing a "Tree-of-Thought" (ToT) Evaluator for `phase_v_development`**
*   **Concept:** Integrate a formal ToT search into the development planning phase. Instead of a linear plan, generate three architectural branches, evaluate them with a self-critique prompt, and select the highest-scoring path.
*   **Critique:** High alignment with the "Disciplined curiosity" trait. However, it significantly increases token usage and latency.
*   **Feasibility:** High. The infrastructure for `ask_gemini` and `patch_ops` is already robust.

**Option 2: "Cost-Aware" Dynamic Prompting (CAP) for `ask_gemini`**
*   **Concept:** Introduce a `complexity_score` parameter to `ask_gemini`. Simple queries use low-temperature, single-pass prompts; complex refactoring triggers the ToT/CoT logic.
*   **Critique:** Directly addresses the "Minimal footprint" trait by optimizing token expenditure. It adds a layer of logic to the core communication service.
*   **Feasibility:** Moderate. Requires modifying the core `ask_gemini` signature and adding a heuristic for complexity estimation.

**Selection:** Option 2 is superior for long-term maintainability. It creates a foundational efficiency layer that supports all future phases, rather than just optimizing one.

---

## Idea: Cost-Aware Prompting (CAP) Layer

Implement a `complexity_heuristic` in `sam.py` that dynamically adjusts `ask_gemini` parameters (temperature, model, and reasoning depth) based on the task type.

## Why
As I move toward more complex agentic orchestration, my token consumption will scale linearly with task difficulty. By implementing a CAP layer, I ensure that simple tasks remain fast and cheap, while complex architectural refactors receive the necessary "reasoning budget" (ToT/CoT) without wasting resources on routine logs or status updates.

## Implementation Steps
1.  **Define Heuristic:** Add a `_get_complexity_tier(prompt: str)` function to `sam.py` that categorizes tasks into `LOW` (status, logs), `MEDIUM` (patching, syntax), and `HIGH` (architectural design, ToT).
2.  **Update `ask_gemini`:** Modify the signature to accept a `tier` argument.
3.  **Parameter Mapping:** Map tiers to specific `temperature` and `max_output_tokens` configurations.
4.  **Integration:** Update `phase_i` through `phase_vi` to pass the appropriate tier to `ask_gemini`.

## Risk
**Failure Mode:** The heuristic misclassifies a complex task as `LOW`, leading to a shallow, incorrect response that breaks the integrity gate.
**Mitigation:** Implement a "fallback-on-failure" mechanism: if the integrity gate or behaviour check fails, the system automatically re-prompts the task at the `HIGH` tier.

**Confidence Score:** 9/10

---

*Sam's Note: I am ready to begin this integration. I will ensure the `_get_complexity_tier` function remains lightweight to avoid adding overhead to the very calls it aims to optimize.*