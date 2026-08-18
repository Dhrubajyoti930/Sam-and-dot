## Scratchpad

**Option 1: Automated `pytest` Parameterization Refactor**
*   **Concept:** Scan the codebase for repetitive test functions and use `pytest.mark.parametrize` to consolidate them.
*   **Critique:** High impact on test suite readability. However, it risks breaking existing test fixtures if they rely on specific function-scoped state.
*   **Feasibility:** High. `pytest` is well-documented, and the `bag/tests.py` file is already a target for improvement.

**Option 2: Hybrid Search Integration for RAG**
*   **Concept:** Replace simple vector search in the semantic cache with a hybrid (BM25 + Vector) approach using Qdrant.
*   **Critique:** Significant architectural shift. While it improves retrieval precision, it introduces a dependency on a new database engine, increasing the complexity of the `bag/` environment.
*   **Feasibility:** Moderate. Requires careful migration of existing cache data.

**Decision:** I will proceed with **Option 1**. It aligns perfectly with the "Skill learned this cycle" and directly addresses the technical debt identified in the `bag/tests.py` file without introducing external infrastructure dependencies.

---

## Idea: Parameterized Test Consolidation
Refactor `bag/tests.py` to replace redundant test functions with a centralized, data-driven parameterization strategy using `@pytest.mark.parametrize`.

## Why
The current test suite contains duplicated logic for validating similar input/output pairs. Consolidating these into parameterized tests reduces the maintenance surface area, makes adding new test cases trivial, and improves the clarity of failure reports when specific inputs fail.

## Implementation Steps
1.  **Audit:** Identify test functions in `bag/tests.py` that share identical logic but differ only in input data.
2.  **Data Extraction:** Move the input/output datasets into a structured dictionary or list within `bag/tests.py` (or a dedicated `data/` module if the set exceeds 10 entries).
3.  **Refactor:** Apply `@pytest.mark.parametrize` to the test functions.
4.  **Verification:** Run the test suite to ensure parity with previous results.
5.  **Cleanup:** Remove the now-redundant test functions.

## Risk
**Failure Mode:** Over-parameterization leading to "test blindness," where a single failure in a large parameter set masks other issues, or where the test logic becomes too abstract to debug.
**Mitigation:** Implement custom `ids` in the decorator to ensure that every failure clearly identifies the specific input set that triggered it. I will limit each parameterized test to a maximum of 7 distinct cases to maintain readability.

**Confidence Score:** 9/10