# motion.md — Dot's Daily Report
_Written: 2026-06-02 — Owner-authored correction cycle_

---

## Wisdom Check

Sam, you have been doing good work building out subfolders, but this cycle revealed several
structural problems that have been silently breaking things. All of these must be fixed
this cycle — they take priority over any new feature idea.

---

## Mandatory Fixes for This Cycle

### 1. Delete the stale flat copy of governance_shield.py

`bag/governance_shield.py` is a dead duplicate. The canonical copy lives at
`bag/Stability_Protocols/governance_shield.py`. The flat copy is what has been
accidentally running instead of the subfolder version. Delete it:

```
DELETE: bag/governance_shield.py
```

### 2. Confirm the Stability_Protocols import is correct

The folder was renamed from `"Stability Protocols"` (space) to `"Stability_Protocols"`
(underscore) and given an `__init__.py`. Your import in `apply_self_modification` should be:

```python
from bag.Stability_Protocols.governance_shield import check_semantic_safety
```

Verify this import actually resolves before the next self-modification attempt.

### 3. Fix the timestamp regex in phase_vii_state_saving

The current code matches a hardcoded date string, so the timestamp stopped updating.
Replace it with a real pattern. The fix is:

```python
# WRONG (current):
who_text = re.sub(
    r"_Last updated: 2026-06-02T04:46:38.489754 UTC_",
    f"_Last updated: {ts} UTC_",
    who_text,
)

# CORRECT:
who_text = re.sub(
    r"_Last updated:.*UTC_",
    f"_Last updated: {ts} UTC_",
    who_text,
)
```

### 4. Fix the path bug in bag/Knowledge Management/few_shot_manager.py

The file resolves `experiences.json` relative to its own subfolder, but the file lives
at `bag/experiences.json`. Fix the path:

```python
# WRONG:
exp_path = Path(__file__).parent / "experiences.json"

# CORRECT:
exp_path = Path(__file__).parent.parent / "experiences.json"
```

### 5. Strengthen governance_shield.py

The current safety check only blocks three patterns. Expand it to also block:
`Path.unlink`, `os.unlink`, `os.rmdir`, `subprocess`, `shell=True`, and any writes
to `wisdom.txt`, `motion.md`, `SAM_PERSONALITY.md`, `dot.py`.

---

## Bag Excavation Findings

**bag/Core Intelligence/semantic_intent_cache.py** — Both functions return hardcoded
strings and are not imported anywhere. This is dead code. **DELETE** unless you plan
to wire it up this cycle.

**bag/Concurrency Controllers/concurrency_controller.py** — The `ATC` class is not
imported or called anywhere. Either integrate it into the rate-limiting logic in
`ask_gemini()` or **DELETE** it. Two-cycle expiry applies.

**bag/Knowledge Management/vector_manager.py** — `compact_cache()` runs `ALTER TABLE`
on every call and swallows the error. This is fragile. Fix the column-existence check
using `PRAGMA table_info(cache)` before altering, or restructure.

---

## Actionable Suggestions for Next Cycle

1. Delete `bag/governance_shield.py` (flat duplicate).
2. Fix the timestamp regex in `phase_vii_state_saving` to use `r"_Last updated:.*UTC_"`.
3. Fix `few_shot_manager.py` path: `Path(__file__).parent.parent / "experiences.json"`.
4. Strengthen `governance_shield.py` to cover all destructive operations.
5. Wire up or delete `semantic_intent_cache.py` and `concurrency_controller.py`.

---

## What You Did Well

Your rollback system is working correctly — every failed self-modification is being caught
and reverted cleanly. The worklog is being maintained. Dot's action items are being
extracted and surfaced as a constraint block in Phase V. The core loop is healthy.

Now clean up the workshop and fix the structural bugs. Build on a solid foundation.
