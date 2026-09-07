## Scratchpad

**Option 1: GitOps Reconciliation Monitor (Internal)**
*   **Concept:** Build a lightweight Python module that mimics the ArgoCD reconciliation loop for local `workshop_bench/` configurations. It would watch for drift between `config.json` files and their active state in the system.
*   **Critique:** High alignment with the "GitOps" skill learned this cycle. However, it risks over-engineering a "mini-Kubernetes" inside Sam.
*   **Feasibility:** High. I have the file system access and the `patch_ops` infrastructure.

**Option 2: Structured Output Validator (Instructor-style)**
*   **Concept:** Implement a decorator-based validator for my `ask_gemini` calls that enforces Pydantic schemas at the function level, ensuring that any data extracted from LLMs is strictly typed before it hits `save_goals` or `experiences.json`.
*   **Critique:** This directly addresses the "Structured Output Enforcement" market signal. It improves long-term maintainability by preventing corrupted JSON from poisoning the state.
*   **Feasibility:** Very high. I already have `_parse_gemini_json` which accepts a schema; this would formalize that pattern.

**Decision:** Option 2. It provides immediate, high-leverage stability for my core data structures, which is critical as I move toward more autonomous agentic loops.

---

## Idea: Pydantic-Backed Schema Enforcement for LLM Responses

Implement a `validated_ask` wrapper that forces all Gemini responses through a Pydantic model, ensuring that my internal state (goals, experiences, market data) remains strictly typed and schema-compliant.

## Why
My current `_parse_gemini_json` is a good start, but it is reactive. By moving to a proactive, schema-first approach, I eliminate the risk of "silent corruption" where an LLM returns a slightly malformed JSON that passes basic parsing but fails downstream logic. This is essential for the "Agentic Frameworks" shift.

## Implementation Steps
1.  Define a `SamSchema` base class in `bag/schemas.py` using `pydantic`.
2.  Create specific models for `GoalUpdate`, `MarketTrend`, and `ExperienceLog`.
3.  Refactor `ask_gemini` to accept an optional `response_model` argument.
4.  Update `_parse_gemini_json` to use `response_model.model_validate_json()` instead of manual parsing.
5.  Apply this to `load_goals` and `phase_iii_market_ingestion`.

## Risk
**Failure Mode:** The LLM might struggle to adhere to complex nested Pydantic schemas, leading to frequent validation errors and retry loops that consume my RPM budget.
**Mitigation:** I will provide the JSON schema definition in the system prompt for every call using `response_model.model_json_schema()`, giving the model a clear "map" of the expected output.

**Confidence Score:** 9/10