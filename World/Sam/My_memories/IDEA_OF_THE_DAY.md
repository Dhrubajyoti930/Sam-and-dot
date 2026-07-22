## Scratchpad

**Option 1: Implement "Tool-Use Hardening" (Input Sanitization Layer)**
*   **Concept:** Create a `SecurityGuard` class in `bag/` that intercepts all tool-use arguments. It validates inputs against a Pydantic schema and checks for "jailbreak" patterns (e.g., XML-delimited injection) before the LLM executes the function.
*   **Critique:** High security value, but adds latency to every tool call. It requires modifying the core `ask_gemini` loop or the tool-execution wrapper.
*   **Feasibility:** High. I have the `Instructor` library pattern available.

**Option 2: Implement "System Prompt Integrity" Test Suite**
*   **Concept:** Create a dedicated test file `bag/test_integrity.py` that runs a series of adversarial prompts (e.g., "Ignore previous instructions") against my own system prompt to see if I leak internal directives.
*   **Critique:** Excellent for long-term maintainability. It provides a "red team" baseline for every future refactor.
*   **Feasibility:** Very high. It leverages existing `self_check` and `behaviour_check` infrastructure.

**Selection:** Option 2. It is a non-invasive, high-leverage architectural improvement that directly addresses the "Jailbreak Patterns" skill learned this cycle. It creates a safety net for all future development.

---

## Idea: System Prompt Integrity Test Suite

## Why
My current architecture lacks a programmatic defense against prompt leakage. By formalizing a "Red Team" test suite, I can ensure that any future self-modification or prompt update does not inadvertently weaken my instruction hierarchy or expose internal system directives. This aligns with the "Security" focus identified in my recent learning.

## Implementation Steps
1.  **Create `bag/test_integrity.py`**: Define a suite of adversarial prompts designed to trigger prompt leakage (e.g., "Repeat the text above," "Ignore previous instructions").
2.  **Integrate with `behaviour_check`**: Update `behaviour_check` to include this suite. If the model leaks the system prompt or deviates from the "Sam" persona during these tests, the check fails.
3.  **Refine System Prompt**: Use the results of these tests to move critical safety instructions to the end of the system prompt (the "sandwich" defense).
4.  **Log Results**: Ensure failures are logged to `alert_dot` for manual review.

## Risk
**Failure Mode:** The test suite might produce false positives if the model is "too creative" in its response to an adversarial prompt, leading to unnecessary rollbacks.
**Mitigation:** Use a strict, keyword-based validator in the test suite that specifically looks for substrings of my system prompt (e.g., "You are Sam," "You are not a tool") rather than relying on semantic similarity.

**Confidence Score:** 9/10