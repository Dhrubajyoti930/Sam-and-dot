## Scratchpad

**Option 1: Implement a "Composite Action" Registry for CI/CD**
*   **Concept:** Create a `bag/actions/` directory containing reusable composite actions for common tasks (e.g., `lint-and-test`, `semantic-check`).
*   **Critique:** High leverage for long-term maintainability. It standardizes the environment across the repo. However, it requires modifying the `.github/workflows/` files, which are outside the immediate `sam.py` scope.
*   **Feasibility:** High. I have the skill (Composite Actions) and the infrastructure (patching).

**Option 2: Introduce a "Schema-First" Event Bus**
*   **Concept:** Replace the current loose event-handling with a Pydantic-validated event bus. Every event must conform to a specific `BaseEvent` schema.
*   **Critique:** Excellent for system stability and debugging. However, it is a significant refactor of existing logic. It might be "over-engineering" if the current event flow is not yet causing friction.
*   **Feasibility:** Moderate. Requires careful migration to avoid breaking existing state.

**Selection:** Option 1. It directly addresses the "Action Items" identified in the market scan and aligns with my goal of reducing technical debt through modular, reusable logic.

---

## Idea: Standardized CI/CD Composite Action Registry

Implement a `bag/ci/` directory containing a `standard-setup` composite action. This action will encapsulate the environment initialization, dependency installation, and linting steps currently duplicated across workflow files.

## Why
Currently, my CI/CD logic is fragmented. By centralizing the "opinionated" setup into a composite action, I ensure that every workflow uses the exact same environment configuration. This reduces the risk of "drift" where one workflow passes while another fails due to subtle environment differences. It also makes future updates to the build process a single-file change.

## Implementation Steps
1.  **Create Directory:** Create `bag/ci/standard-setup/` and `bag/ci/standard-setup/action.yml`.
2.  **Define Action:** Populate `action.yml` with the standard `runs: using: "composite"` block, including steps for `actions/setup-python`, dependency installation, and a `ruff` check.
3.  **Refactor Workflows:** Update existing `.github/workflows/*.yml` files to use `uses: ./bag/ci/standard-setup` instead of the current multi-step shell blocks.
4.  **Validation:** Run `self_check()` to ensure the new directory structure doesn't interfere with existing path resolution.

## Risk
**Failure Mode:** The composite action might fail to resolve paths correctly if the `uses` path is not correctly interpreted by the runner, or if the environment variables (like `PYTHONPATH`) are not correctly inherited.
**Mitigation:** I will perform a dry-run by creating a test workflow that calls the action before migrating the primary production workflows. I will also use absolute paths relative to `${{ github.workspace }}` within the action to ensure robustness.

**Confidence Score:** 9/10