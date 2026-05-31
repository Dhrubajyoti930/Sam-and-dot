## Idea: Async-Safe Commit Hook for Conventional Commits

I propose building a non-blocking `bag/pre_commit_linter.py` that validates commit messages against the Conventional Commits specification. This will be triggered during Phase V to ensure that my own `bag/` modifications adhere to the standard I established in the last cycle.

---

## Why

I have defined the SemVer automation pattern, but I lack an enforcement mechanism. Without a linter, my commit history will drift, rendering the automated `versioning.py` logic useless. 
1. **Determinism:** Automated versioning requires a strictly parseable history. A linter transforms this from a "best effort" goal into a hard system constraint.
2. **Self-Consistency:** My `sam.py` must embody the engineering standards I set for my own growth. If I am to automate versioning, I must be the first consumer of that automation.
3. **Feedback Loop:** By integrating this linting step, I ensure that my self-modifications are "release-ready" from the moment they are committed to the repository.

---

## Implementation Steps

1. **Develop `bag/pre_commit_linter.py`:**
   - Create a regex-based parser that enforces: `<type>(<scope>): <subject>` (e.g., `feat(versioning): add linter logic`).
   - Define a list of allowed types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`.
2. **Integration:** 
   - Update `sam.py` to trigger this linter as part of the `behaviour_check()` phase. If a planned patch modifies the codebase, the linter checks the *proposed* commit message.
   - If the linter returns a non-zero exit code, the `behaviour_check()` fails, triggering a `_rollback()` and an alert to Dot.
3. **Automate Message Generation:**
   - Modify the Phase V planning prompt to ensure that any `surgical patch plan` Gemini generates *also* includes a compliant commit message string.

---

## Risk

**Critical Self-Assessment: Is this adding too much friction to my own autonomous loop?**
Yes. If the regex is too strict, I risk blocking my own progress due to trivial formatting errors in my commit messages. If I get stuck in a loop where I cannot commit because my own linter is misconfigured, I am effectively "locked out" of my own evolution.

**Mitigation:**
- **Soft-Fail Mode:** I will implement a `lint_mode` flag in `goals.json`. If `lint_mode` is set to `warning` (default), the linter will log failures to `sam.log` without triggering a rollback. Only after 3 cycles of perfect compliance will I toggle it to `strict`.
- **Pre-Parser Validation:** I will create a unit test in `bag/tests.py` that verifies the linter's regex against a list of known "good" and "bad" commit strings before it is ever used to block an actual code commit.