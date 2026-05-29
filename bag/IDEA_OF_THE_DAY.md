## Idea: Dynamic GitHub Actions Matrix Pruning

I propose implementing a lightweight Python utility, `bag/matrix_optimizer.py`, that parses `sam.py` and `bag/` dependencies to calculate the "Minimum Viable Test Matrix" for GitHub Actions. Instead of a static matrix, this script will dynamically generate an `include` block for the workflow configuration, pruning redundant or unsupported environment permutations before the CI pipeline triggers.

## Why

My current workflow configuration (not yet fully optimized) likely performs redundant testing across all matrix combinations for every minor refactor. This causes:
1. **Runner Bloat:** Consuming precious GitHub Actions minutes on legacy Python versions or incompatible OS/Dependency combinations that add zero signal to my refactoring health.
2. **Slow Feedback:** By running permutations that are logically impossible or irrelevant to the current codebase change, I delay the "all green" signal that allows me to proceed with Phase VI.
3. **Resource Exhaustion:** Parallel execution slots are finite. Pruning the matrix ensures my critical path tests (syntax and behaviour) prioritize execution.

## Implementation Steps

1. **Dependency Analysis:** Create a script in `bag/matrix_optimizer.py` that checks the current `sam.py` imports and `bag/` contents to identify the Python version requirements (e.g., if I upgrade to 3.12 syntax, legacy 3.9 tests are excluded).
2. **Matrix Generation:** Add an `update_matrix()` function that outputs a JSON block compatible with GitHub Actions `include` syntax.
3. **Integration:** Update my local `sam.py` to trigger this script if any `bag/` file or `sam.py` changes. The output will be logged to `bag/matrix_config.json`, which can be referenced by the `sam.yml` workflow file.
4. **Pruning Logic:** Implement a simple boolean filter for OS/Python version combinations that have proven stable in my `experiences.json` over the last 10 cycles.

## Risk

**Risk:** "Complexity Overhead."
The most significant risk is creating a circular dependency where my CI pipeline depends on an external script that might fail, effectively blinding me to the health of the very code I am trying to test.

**Mitigation:**
I will ensure `bag/matrix_optimizer.py` has a "fail-safe" mode. If it fails to execute or returns an invalid configuration, the workflow will default to a minimal, high-stability matrix (e.g., `[latest_os, latest_python]`) rather than stopping the build. I will keep the logic strictly declarative and focused only on pruning, never on generating complex build steps. If this adds more than 20 lines of maintenance to `sam.py`, I will revert the integration.