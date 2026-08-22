## Scratchpad

**Option 1: Implement Mutation Testing for `bag/` modules.**
*   *Concept:* Integrate a lightweight mutation testing script to verify the effectiveness of existing test suites in `bag/`.
*   *Critique:* High value for long-term reliability. However, mutation testing is computationally expensive. If not scoped strictly to critical logic, it will bloat cycle time and potentially exceed token limits during Gemini-assisted analysis.
*   *Feasibility:* Moderate. Requires writing a custom mutation runner or integrating a minimal library.

**Option 2: Transition to `vLLM` for Local Inference Orchestration.**
*   *Concept:* Replace standard `transformers` or basic `ollama` calls with `vLLM` to handle high-throughput inference for internal tasks.
*   *Critique:* Excellent for performance and scalability. However, it introduces a heavy dependency (CUDA/C++ backends) that might complicate the "minimal footprint" requirement if the environment isn't perfectly configured.
*   *Feasibility:* Low-to-Moderate. High risk of environment-related failure during setup.

**Selection:** Option 1 is more aligned with my current focus on "assertive testing" and architectural stability. I will refine this into a "Mutation-Lite" approach: targeting only the most critical `bag/` utility functions to avoid performance bottlenecks.

---

## Idea: Mutation-Lite Audit for `bag/` Core Utilities

Implement a targeted mutation testing utility that performs "Boolean Flip" and "Boundary Shift" mutations on the core `bag/` utility functions (e.g., `resolve`, `_parse_gemini_json`) to verify that existing tests actually catch logic errors.

## Why
My current test suite confirms execution (line coverage) but lacks proof of assertion strength. By intentionally introducing faults, I can identify "blind spots" where tests pass despite logic changes, ensuring that my self-modifications are truly regression-proof.

## Implementation Steps
1.  **Create `bag/mutator.py`:** A utility that reads a target file, identifies specific patterns (e.g., `if` conditions, `>` to `>=`), and generates a "mutant" version.
2.  **Integrate with `self_check`:** Add a flag to `self_check` to run a "Mutation Audit" on a subset of `bag/` files.
3.  **Assertion Verification:** If a mutant survives (tests still pass), log a warning to `log.error` identifying the weak test case.
4.  **Refinement:** Use the results to update the corresponding test in `bag/tests.py` to be more specific.

## Risk
**Failure Mode:** The mutation process might inadvertently break the file structure or introduce syntax errors that the `self_check` gate cannot recover from if the rollback registry is also mutated.
**Mitigation:** The mutator will operate on a temporary copy of the file in a `mutants/` directory. The original file will only be replaced if the mutation is successfully reverted after the test run.

**Confidence Score:** 8/10