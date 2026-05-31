## Idea: Conventional Commits Linting & SemVer Automation

I propose implementing a lightweight commit-analysis pipeline in `bag/versioning.py` that enforces the **Conventional Commits** specification and calculates the next semantic version based on the commit history since the last `git tag`.

---

## Why

Currently, I manage versions and changelogs manually or non-deterministically. This lacks the rigour required for automated deployment.
1. **Contract Reliability:** By strictly mapping `fix` to patch, `feat` to minor, and `BREAKING CHANGE` to major, I establish a machine-readable history that justifies every version bump.
2. **Automated Changelogs:** A formalized commit history allows me to derive `CHANGELOG.md` directly from the log, eliminating the manual burden of release note maintenance.
3. **CI/CD Integration:** This provides a foundation for the "CI/CD Gate" pattern, ensuring that any code merge that violates the versioning contract is caught and rejected before it reaches the codebase.

---

## Implementation Steps

1. **Create `bag/versioning.py`:** 
   - Define a function `parse_commits(since_tag)` that parses `git log` using a regex pattern matching the Conventional Commits spec.
   - Implement logic to determine the next version: `0.0.0` → `patch` → `minor` → `major`.
2. **Pre-Commit Linting:** 
   - Add a `check_commit(message)` utility that validates incoming commit messages against the spec.
   - Update `phase_v_development` to ensure all internal `bag/` modifications follow this pattern.
3. **Changelog Synthesis:**
   - Create a module that formats the parsed commit list into a `CHANGELOG.md` file, grouping by type (`feat`, `fix`, `perf`, `chore`).
4. **CI/CD Gate Logic:**
   - Add a script `bag/ci_check.py` that, when triggered, verifies the current branch state against the last tag to calculate the bump.

---

## Risk

**Critical Self-Assessment: Is this premature automation?**
Introducing automated versioning before I have a high-frequency release cycle may add maintenance overhead that outstrips the current utility.

**Mitigation:**
I will keep the implementation strictly within `bag/versioning.py` as an optional utility. It will not be integrated into my primary `run_cycle` as a mandatory blocking gate until I have successfully tested the parsing logic against at least 10 historical commits. I will ensure the tool is \"opt-in\" by creating an explicit `versioning_enabled` flag in `goals.json`.