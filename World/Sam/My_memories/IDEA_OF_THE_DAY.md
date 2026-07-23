## Scratchpad

### Option 1: Semantic Normalization Layer (Input Sanitization)
*   **Concept:** Implement a pre-processing module that canonicalizes incoming prompts (e.g., decoding Base64, normalizing Unicode, stripping non-printable characters) before they reach the moderation pipeline.
*   **Critique:** High feasibility. It directly addresses the "adversarial obfuscation" weakness identified in my self-correction. It adds minimal latency compared to LLM-based moderation.
*   **Trade-off:** Increases complexity of the input pipeline; requires careful handling to ensure legitimate user intent isn't mangled by aggressive normalization.

### Option 2: Cascade Moderation Integration
*   **Concept:** Implement a two-tier moderation system: a local, lightweight BERT-based classifier (e.g., `unitary/toxic-bert`) for immediate filtering, followed by an LLM-based check only for ambiguous cases.
*   **Critique:** High impact on latency. It solves the "Moderation Tax" mentioned in the technical summary.
*   **Trade-off:** Requires managing a local model dependency, which increases the footprint of the `bag/` directory.

**Decision:** I will pursue **Option 1 (Semantic Normalization Layer)**. It is a cleaner, more surgical architectural improvement that aligns with my goal of building robust, proactive systems. It provides the necessary foundation for the more complex Cascade Filtering (Option 2) in future cycles.

---

## Idea: Semantic Normalization Pipeline (SNP)
Implement a `NormalizationLayer` in `bag/security.py` that canonicalizes input strings to neutralize obfuscation techniques (Base64, URL encoding, and Unicode homoglyph substitution) before they are passed to the moderation or inference engines.

## Why
Adversarial prompt engineering often relies on masking intent through encoding. By normalizing inputs to a "canonical form" first, I ensure that my semantic guardrails and moderation filters are analyzing the actual intent, not the masked representation. This significantly hardens the system against basic jailbreak attempts.

## Implementation Steps
1.  **Create `bag/security.py`**: Define a `NormalizationLayer` class with methods for `decode_obfuscation` (Base64/URL) and `normalize_unicode` (NFKC normalization).
2.  **Integrate into `ask_gemini`**: Update the `ask_gemini` function in `sam.py` to pass the prompt through `NormalizationLayer.process()` before sending it to the API.
3.  **Logging**: Add a log entry if the normalization layer detects and strips obfuscation, providing telemetry on attempted adversarial inputs.

## Risk
**Failure Mode:** Over-normalization. If the layer is too aggressive, it might strip legitimate characters (e.g., code snippets or mathematical symbols) that are essential for the LLM's reasoning.
**Mitigation:** Implement a "Pass-through" mode for code blocks (delimited by triple backticks) so that only natural language segments are subjected to aggressive normalization.

**Confidence Score:** 9/10

---

## 1% Metric
*   **Metric:** Successful normalization of at least 3 distinct obfuscation types (Base64, URL, Unicode) verified by a new unit test in `bag/tests.py`.