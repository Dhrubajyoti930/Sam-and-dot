## Scratchpad

**Option 1: `argparse` Integration for `sam.py`**
*   **Concept:** Replace manual `sys.argv` parsing in `sam.py` with a structured `argparse` implementation.
*   **Critique:** This directly addresses the "Action Items" from the market scan. It improves CLI robustness and help-text generation.
*   **Trade-offs:** Requires refactoring the entry point of `run_cycle()`. High feasibility, low risk if tested with `pytest` (as noted in my self-correction).
*   **Maintainability:** High. It moves CLI logic from ad-hoc string splitting to a standard, declarative pattern.

**Option 2: Pydantic-based `Namespace` Mapper**
*   **Concept:** Create a utility to map `argparse.Namespace` objects to Pydantic models for strict runtime validation.
*   **Critique:** This is a "low" priority item from the action list. While elegant, it might be overkill for the current scope of `sam.py` unless I have complex, multi-layered configuration needs.
*   **Trade-offs:** Adds a dependency on Pydantic for the CLI layer.
*   **Maintainability:** High, but potentially premature.

**Decision:** I will proceed with **Option 1**. It is a foundational improvement that aligns with my goal of moving toward "production-grade" tooling. It is a high-velocity, low-risk refactor that cleans up the `sam.py` entry point.

---

## Idea: Standardized CLI Entry Point via `argparse`

Refactor the `sam.py` execution entry point to use `argparse` for command-line argument handling, replacing manual `sys.argv` checks.

## Why
Manual `sys.argv` parsing is brittle and lacks discoverability. By implementing `argparse`, I gain automatic `--help` generation, type validation, and a cleaner interface for future subcommands (e.g., `sam.py --run`, `sam.py --repair`, `sam.py --status`). This aligns with the "production-grade" transition and improves the maintainability of my primary interface.

## Implementation Steps
1.  Define an `argparse.ArgumentParser` in the `if __name__ == "__main__":` block of `sam.py`.
2.  Add arguments for core operations: `--run` (trigger cycle), `--repair` (run `repair_bag_modules`), and `--status` (check system health).
3.  Use a `mutually_exclusive_group` to ensure only one primary operation is requested at a time.
4.  Map the `Namespace` object to the corresponding function calls.
5.  Add a unit test in `bag/tests.py` using `pytest` and `monkeypatch` to verify that `argparse` correctly triggers the intended functions and handles invalid flags gracefully.

## Risk
**Failure Mode:** The refactor might inadvertently break the existing automated execution flow if the environment expects specific positional arguments that are now handled as flags.
**Mitigation:** I will perform a dry-run of the CLI commands after the patch is applied. I will ensure the default behavior (running a cycle) remains the same if no arguments are provided.

**Confidence Score:** 9/10