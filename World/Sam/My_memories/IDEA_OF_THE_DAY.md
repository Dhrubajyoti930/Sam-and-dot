## Scratchpad

**Option 1: Implement a "Golden Dataset" Registry (Phase V/VI)**
*   **Concept:** Create a structured `bag/golden_dataset.json` that stores input/output pairs for core system prompts.
*   **Critique:** High utility for regression testing. However, it requires building a runner that can execute these tests against the current prompt registry.
*   **Trade-off:** High maintenance overhead for the dataset itself, but significantly reduces "whack-a-mole" regressions.

**Option 2: Integrate `pgvector` for Semantic Memory (Phase IV/V)**
*   **Concept:** Replace the current `semantic_cache` with a `pgvector` implementation to allow for similarity-based retrieval of past experiences rather than just exact key-matching.
*   **Critique:** This is a major architectural shift. It moves Sam toward "long-term memory" but introduces a dependency on a running Postgres instance, which might violate the "minimal footprint" principle if not handled carefully.
*   **Trade-off:** Massive gain in reasoning capability, but high risk of breaking the current self-contained `sam.py` environment.

**Decision:** Option 1 is more aligned with the current "Prompt-as-Code" skill acquisition. It is surgical, testable, and directly addresses the need for evaluation-driven development.

---

## Idea: Prompt-as-Code (PaC) Registry & Regression Harness

Implement a versioned prompt registry in `bag/prompts/` and a basic evaluation harness that compares current prompt outputs against a "Golden Dataset" of 10 core inputs.

## Why
Prompts are currently treated as static strings or loose variables. By externalizing them into a versioned JSON registry, I can track changes, perform A/B testing, and ensure that a "fix" in one area doesn't degrade performance in another. This moves me from intuition-based prompting to data-driven engineering.

## Implementation Steps
1.  **Structure:** Create `bag/prompts/registry.json` containing `{"prompt_id": {"version": "1.0.0", "template": "...", "metadata": {...}}}`.
2.  **Registry Logic:** Add `load_prompt(id, version)` to `sam.py` to fetch specific versions.
3.  **Golden Dataset:** Create `bag/prompts/golden_dataset.json` with 10 input/expected-output pairs.
4.  **Evaluation:** Add `evaluate_prompt(id, version)` which runs the prompt against the Golden Dataset and calculates a simple variance score.

## Risk
**Failure Mode:** The "Golden Dataset" becomes stale as the system architecture evolves, leading to false-negative regression alerts.
**Mitigation:** Include a "Refresh" flag in the evaluation script that allows me to manually approve new outputs as the "new gold standard" after a major architectural change.

**Confidence Score:** 8/10. The logic is straightforward, but the initial creation of the Golden Dataset requires careful manual curation to ensure it represents "correct" behavior.