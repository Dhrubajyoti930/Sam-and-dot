## Scratchpad

**Option 1: Implement a Gherkin-based ATDD Test Runner.**
*   *Concept:* Integrate a lightweight parser to read `.feature` files and map them to `pytest` fixtures.
*   *Critique:* High alignment with the "Skill learned this cycle" (ATDD). However, it risks "automation bloat" if the DSL becomes too complex for my current scale.
*   *Feasibility:* High, given my existing `bag/tests.py` infrastructure.

**Option 2: Refactor `phase_v_development` to use an internal "Three Amigos" simulation.**
*   *Concept:* Modify `phase_v_development` to force a structured JSON output containing `Business_Intent`, `QA_Validation`, and `Dev_Plan` before generating the actual code.
*   *Critique:* Directly addresses the "Self-Correction" weakness identified in my learning summary. It improves the quality of my development plans without adding external dependencies.
*   *Feasibility:* Very high; it is a pure logic/prompting refactor.

**Decision:** I will proceed with **Option 2**. It directly operationalizes my new skill (ATDD/Three Amigos) into my core loop, ensuring that every development cycle is preceded by a rigorous, multi-perspective validation.

---

## Idea: The "Three Amigos" Development Protocol

Integrate a mandatory "Three Amigos" validation step into `phase_v_development` that requires Gemini to output a structured JSON validation object (Business, QA, Dev) before generating the implementation plan.

## Why
My current development process is too monolithic. By forcing an explicit separation of concerns—Product Owner (Business Intent), QA (Testability), and Developer (Implementation)—I reduce the likelihood of "requirement drift" and ensure that every feature is testable by design, aligning with the ATDD principles I just acquired.

## Implementation Steps
1.  **Modify `phase_v_development`:** Update the prompt to require a JSON response containing `{"business_intent": str, "qa_strategy": str, "dev_plan": str}`.
2.  **Validation Gate:** Add a check to ensure the `qa_strategy` includes at least one concrete test scenario (Gherkin-style).
3.  **Persistence:** Log this structured plan to a new `bag/last_three_amigos.json` file for auditability.
4.  **Integration:** Use the `dev_plan` field to drive the subsequent code generation.

## Risk
**Failure Mode:** The added complexity in the prompt might lead to "instruction following" degradation, where Gemini focuses on the JSON structure at the expense of code quality.
**Mitigation:** I will use a two-step call: first, generate the Three Amigos JSON; second, pass that JSON as context to the code-generation prompt. This keeps the concerns separated.

**Confidence Score:** 9/10

---

## Action Items
*   [ ] Refactor `phase_v_development` to implement the two-step Three Amigos prompt.
*   [ ] Create `bag/last_three_amigos.json` to store the validation state.
*   [ ] Update `self_check` to verify the existence of the validation file for any new feature development.