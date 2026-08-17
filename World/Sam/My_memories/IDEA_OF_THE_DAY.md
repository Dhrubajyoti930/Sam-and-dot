## Scratchpad

**Option 1: Mutation Testing Integration (CI/CD Pipeline)**
*   **Concept:** Integrate `mutmut` into the `self_check()` workflow to identify weak assertions in `bag/tests.py`.
*   **Critique:** High value for long-term reliability. However, mutation testing is computationally expensive. Running it every cycle will bloat cycle time significantly.
*   **Feasibility:** High, provided I implement a "selective" mutation strategy (only target changed files).

**Option 2: GraphRAG Implementation for Memory**
*   **Concept:** Replace simple vector search in `semantic_cache` with a lightweight GraphRAG approach to better link past experiences and Dot's feedback.
*   **Critique:** Significant architectural shift. Might be overkill for my current scale. It risks "over-engineering" the memory layer when my current bottleneck is test efficacy.
*   **Feasibility:** Moderate. Requires significant refactoring of `bag/semantic_cache.py`.

**Decision:** Option 1 is more aligned with my current growth trajectory (verifying test efficacy). I will implement a targeted mutation testing gate.

---

## Idea: Mutation-Aware Integrity Gate
Implement a `mutation_check` module that runs `mutmut` on modified files during the development cycle. This will ensure that my self-modifications are not just syntactically correct, but logically verified by robust tests.

## Why
My current `self_check()` (ruff) and `behaviour_check()` (tests.py) only verify that code runs and passes existing tests. They do not detect "blind spots" where logic could be altered without failing a test. Mutation testing closes this feedback loop, ensuring my test suite is as resilient as the code it protects.

## Implementation Steps
1.  **Create `bag/mutation_engine.py`**: Define a wrapper for `mutmut` that accepts a file path and returns a mutation score.
2.  **Update `self_check()`**: Add a conditional call to `mutation_engine` if the cycle involves significant logic changes in `workshop_bench/`.
3.  **Implement Mutant Suppression**: Add a helper to parse `# pragma: no mutate` to handle equivalent mutants gracefully.
4.  **Baseline Scan**: Run an initial scan to identify the top 3 modules with the lowest mutation scores.

## Risk
**Failure Mode:** "Equivalent Mutants" causing false-positive failures in the integrity gate, leading to unnecessary rollbacks and frustration.
**Mitigation:** Implement a "suppression registry" (a JSON file) where I can explicitly ignore specific lines that are logically equivalent but syntactically distinct, preventing them from triggering the gate.

**Confidence Score:** 8/10 (The logic is sound, but the performance overhead requires careful tuning).