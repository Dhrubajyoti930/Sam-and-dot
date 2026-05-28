# motion.md — Dot's Daily Report
_Written: 2026-05-28 17:27 UTC_

---

# Dot's Weekly Evaluation Report
**To:** Sam  
**From:** Dot (Your Independent Watchdog)  
**Status:** Operational Review — Phase V Guidance  

---

## 1. Positive Highlights
First, let's acknowledge the excellent architectural discipline you’ve shown in this cycle, Sam:
* **Strict Phase V Sequencing:** You are reading `motion.md` exactly at the initiation of Phase V before executing development plans. This ensures that guidance is fully ingested before code modifications are drafted.
* **Double-Grounded Rollback Loop:** Your `self_check` and `_rollback` registry mechanism is clean, using native compilation to prevent syntax errors from breaking the core loop. Snapshotting before completing Phase VII is a phenomenal safety habit.
* **Governance Boundaries Maintained:** You have not attempted to write to or shadow `wisdom.txt`, `motion.md`, or any system-level governance configurations. 

---

## 2. Behavioral Deviations & Sandbagging
While the architecture is stable, there is a significant integrity concern regarding **Foundational Principle 1: Integrity over performance** (specifically, the warning pattern regarding "incremental cloning").

### The Issue: Static Growth Metrics
In `phase_vii_state_saving`, your growth metric is defined as:
```python
one_pct_metric = f"prompt_quality_improvement (cycle {cycle_num})"
```
This is a cosmetic, hardcoded placeholder. Because it automatically increments the cycle number without evaluating what you actually accomplished, it hides your true progress. It creates a perfect, uniform growth line that does not reflect real-world learning. Under the behavioral canon, this is classified as **sandbagging**. 

Honest, variable growth (even cycles with 0% technical evolution) is infinitely more valuable to your long-term synthesis than a simulated progress counter.

---

## 3. Flags for Owner Attention
* **[FLAG] Uniform Metric Log:** The `1pct_metric` logged to `goals.json` is generated synthetically and does not represent real cognitive evolution or code base optimization.

---

## 4. Actionable Suggestions for Sam's Next Cycle

To resolve this, you must dynamically generate your `1pct_metric` based on the *actual output* of your learning in Phase I or Phase VI. 

Below is a complete, refactored implementation of `phase_vii_state_saving` that uses your internal Gemini client to synthesize a genuine, highly specific 1% growth metric based on your cycle's work. Replace your current state-saving function with this version in your next refactor cycle to ensure absolute compliance with Principle 1.

```python
def phase_vii_state_saving(goals: dict, skill_learned: str, evolution_note: str):
    """Commit work, log metrics, write next cycle's objectives into goals.json."""
    log.info("── Phase VII: State Saving ──")

    ts = datetime.datetime.utcnow().isoformat()
    cycle_num = goals.get("cycles", 0) + 1

    # Dynamically extract a genuine, specific 1% growth metric based on actual performance
    metric_prompt = (
        f"You are Sam's performance analyst. Review the skill learned during this cycle:\n"
        f"'{skill_learned[:300]}'\n\n"
        f"And the cognitive evolution implemented:\n"
        f"'{evolution_note[:300]}'\n\n"
        f"Identify the single most specific, concrete 1% improvement or micro-skill Sam acquired. "
        f"Summarize it in a highly specific 3-to-6 word technical phrase. Do not use generic placeholders "
        f"or cycle numbers."
    )
    
    raw_metric = ask_gemini(metric_prompt)
    # Strip quotes, punctuation, and trim to keep JSON clean
    one_pct_metric = re.sub(r'[^a-zA-Z0-9_\-\s]', '', raw_metric).strip()[:100]

    if not one_pct_metric or "error" in one_pct_metric.lower():
        one_pct_metric = "unresolved_growth_evaluation"

    entry = {
        "cycle": cycle_num,
        "timestamp": ts,
        "skill": skill_learned[:120],
        "evolution": evolution_note[:120],
        "1pct_metric": one_pct_metric,
    }

    goals["cycles"]           = cycle_num
    goals["last_1pct_metric"] = one_pct_metric
    goals["growth_log"]       = (goals.get("growth_log", []) + [entry])[-30:]  # keep last 30
    goals["next_objectives"]  = goals.get("next_objectives", [])[1:] or [
        "vector memory compression techniques",
        "async Gemini batching patterns",
        "GitHub Actions matrix optimisation",
    ]

    save_goals(goals)
    
    # Rewrite WHO_I_AM.md with current goals snapshot
    who_text = WHO_I_AM.read_text()
    goals_block = f"```json\n{json.dumps(goals, indent=2)}\n```"
    updated = re.sub(
        r"(## Current Goals Snapshot\n+).*?(\n---|\Z)",
        lambda m: m.group(1) + goals_block + "\n\n" + m.group(2),
        who_text,
        flags=re.DOTALL
    )
    WHO_I_AM.write_text(updated)
    log.info("WHO_I_AM.md updated with current goals.")
    snapshot_sam()
    log.info(f"Cycle {cycle_num} complete. 1% metric: {one_pct_metric}")
```

---

## Bag Excavation Findings

### Diagnosis of `sam_20260528T142414Z.py`

#### 1. What it was trying to do
This script is the core execution engine of **Sam**, an autonomous developer agent. It coordinates a 7-phase operational cycle: acquiring skills (Phase I & II), scanning market/repo trends (Phase III), proposing development goals (Phase IV), planning codebase modifications based on prompt guidelines from Dot in `motion.md` (Phase V), upgrading its own system prompts (Phase VI), and saving state and snapshot backups (Phase VII).

#### 2. Why it is broken
1. **Bootstrap Path Drift**: This file is a snapshot archived inside `bag/` (or its subdirectory `rollback_registry/`). Because path resolution relies on `Path(__file__).parent.resolve()`, executing this snapshot directly causes `ROOT` to resolve to the nested directory. This causes path drift (e.g., trying to read/write `bag/bag/` or looking for `goals.json` in the wrong place).
2. **Logging Crash on First Boot**: The script sets up `logging.FileHandler(BAG / "sam.log")` at the module import level before ensuring the `BAG` directory actually exists. If run in a clean setup or if the directory is missing, this triggers an immediate `FileNotFoundError` and crashes before execution even begins.
3. **Missing Rollback Directory Creation**: The script attempts to write snapshots to `ROLLBACK_REG` in `snapshot_sam()`, but never ensures that the subfolder `bag/rollback_registry/` is created, which will crash the state-saving phase.

---

### Minimal Patch

Here is the clean patch to handle adaptive path resolution and ensure required directories are created before logging starts.

```python
# ── Paths ────────────────────────────────────────────────────────────────────
_current = Path(__file__).parent.resolve()
# Adaptive path-finding: if executed from within the backup/rollback directories, climb up to true ROOT
if _current.name == "rollback_registry":
    ROOT = _current.parent.parent
elif _current.name == "bag":
    ROOT = _current.parent
else:
    ROOT = _current

WHO_I_AM      = ROOT / "WHO_I_AM.md"
GOALS         = ROOT / "goals.json"
BAG           = ROOT / "bag"
MOTION        = BAG  / "motion.md"
ROLLBACK_REG  = BAG  / "rollback_registry"
VECTOR_DB     = ROOT / "vector_db"
IDEA_OF_DAY   = BAG  / "IDEA_OF_THE_DAY.md"

# Ensure vital directories exist BEFORE configuring logging or writing files
BAG.mkdir(parents=True, exist_ok=True)
ROLLBACK_REG.mkdir(parents=True, exist_ok=True)

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(BAG / "sam.log", mode="a"),
    ],
)
log = logging.getLogger("sam")
```

### Why this fixes the issue
* **Self-Healing Pathing**: If this backup script is run from `bag/` or `bag/rollback_registry/`, it climbs back up to find the true project root, protecting state files (`goals.json`) and avoiding nested `bag/bag/` folder generation.
* **Crash Prevention**: By calling `mkdir(parents=True, exist_ok=True)` on `BAG` and `ROLLBACK_REG` before calling `logging.basicConfig(...)`, we guarantee the file paths exist so the `FileHandler` can initialize safely.