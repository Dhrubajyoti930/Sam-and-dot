"""
sam.py — Central Intelligence Loop
Project Sam-and-dot: The Autonomous Developer Agent

Operational Lifecycle:
  Phase I   - Deep Learning
  Phase II  - Spaced Repetition
  Phase III - Market & Code Ingestion
  Phase IV  - The Synthesis
  Phase V   - Development & Refactor  (reads motion.md FIRST)
  Phase VI  - Cognitive Evolution
  Phase VII - State Saving
"""

import os
import re
import sys
import json
import time
import datetime
import logging
import logging.handlers
import subprocess
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT            = Path(__file__).parent.resolve()
WHO_I_AM        = ROOT / "WHO_I_AM.md"
SAM_PERSONALITY = ROOT / "SAM_PERSONALITY.md"
GOALS           = ROOT / "goals.json"
BAG             = ROOT / "bag"
MOTION          = BAG  / "motion.md"
WISDOM          = BAG  / "wisdom.txt"
ROLLBACK_REG    = BAG  / "rollback_registry"
VECTOR_DB       = ROOT / "vector_db"
IDEA_OF_DAY     = BAG  / "IDEA_OF_THE_DAY.md"
EXPERIENCES     = BAG  / "experiences.json"
REQUEST_JSON    = BAG  / "request.json"
CYCLE_STATUS    = BAG  / "cycle_status.txt"
TESTS           = BAG  / "tests.py"

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.handlers.RotatingFileHandler(BAG / "sam.log", maxBytes=500_000, backupCount=3),
    ],
)
log = logging.getLogger("sam")

# ── Gemini client ─────────────────────────────────────────────────────────────
from google import genai  # noqa: E402

GEM_KEY = os.environ.get("GEM_KEY_SAM")
if not GEM_KEY:
    raise EnvironmentError("GEM_KEY_SAM secret is not set.")
CLIENT = genai.Client(api_key=GEM_KEY)

MODEL = "gemini-3.1-flash-lite"

# ── Rate limiting ─────────────────────────────────────────────────────────────
# Small pause between sequential Gemini calls to stay within RPM limits.
_CALL_DELAY = 8   # seconds


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def load_goals() -> dict:
    if GOALS.exists():
        with open(GOALS) as f:
            return json.load(f)
    return {
        "cycles": 0,
        "growth_log": [],
        "next_objectives": [
            "vector memory compression techniques",
            "async Gemini batching patterns",
            "GitHub Actions matrix optimisation",
        ],
        "last_1pct_metric": "",
    }


def save_goals(data: dict):
    with open(GOALS, "w") as f:
        json.dump(data, f, indent=2)
    log.info("goals.json updated.")


def load_who_i_am() -> str:
    if WHO_I_AM.exists():
        return WHO_I_AM.read_text()
    return "(WHO_I_AM.md not yet generated)"


def load_personality() -> str:
    if SAM_PERSONALITY.exists():
        return SAM_PERSONALITY.read_text()
    return "(SAM_PERSONALITY.md not found)"


def read_motion() -> str:
    """Sam reads motion.md exactly once — at the top of Phase V."""
    if MOTION.exists():
        return MOTION.read_text()
    return "(motion.md is empty — Dot has not yet written.)"


def load_experiences() -> list:
    if EXPERIENCES.exists():
        with open(EXPERIENCES) as f:
            return json.load(f)
    return []


def save_experiences(data: list):
    with open(EXPERIENCES, "w") as f:
        json.dump(data, f, indent=2)


def ask_gemini(prompt: str, retries: int = 2) -> str:
    """Send a prompt to Sam's Gemini instance. Retries on transient errors."""
    from bag.semantic_cache import check_cache, update_cache
    goals = load_goals()
    cached = check_cache(prompt, goals.get("cycles", 0))
    if cached: return cached

    for attempt in range(retries):
        try:
            response = CLIENT.models.generate_content(
                model=MODEL,
                contents=prompt,
            )
            res = response.text.strip()
            update_cache(prompt, res, goals.get("cycles", 0))
            return res
        except Exception as e:
            err = str(e)
            if "429" in err or "503" in err or "UNAVAILABLE" in err or "RESOURCE_EXHAUSTED" in err:
                wait = _CALL_DELAY * (2 ** attempt)
                log.warning(f"Gemini transient error (attempt {attempt+1}): {e}. Retrying in {wait}s.")
                time.sleep(wait)
            elif "404" in err:
                log.critical("MODEL STRING MAY BE DEPRECATED — owner intervention required.")
                _alert_dot("Gemini returned 404. The model string may be deprecated. Owner must update MODEL in sam.py and bag/dot.py.")
                return "[Gemini error: model not found]"
            else:
                log.error(f"Gemini call failed (non-retryable): {e}")
                return f"[Gemini error: {e}]"
    log.error("Gemini call failed after all retries.")
    return "[Gemini error: exhausted retries]"


def _sleep():
    """Pause between Gemini calls to respect RPM limits."""
    time.sleep(_CALL_DELAY)


def snapshot_sam() -> Path:
    """Archive sam.py and all writable bag/*.py into rollback_registry."""
    ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

    # ── Snapshot sam.py (existing format preserved for backward compat) ──
    dest = ROLLBACK_REG / f"sam_{ts}.py"
    dest.write_text(Path(__file__).read_text())
    log.info(f"Snapshot saved → {dest.name}")

    # ── Snapshot all writable bag/*.py files alongside ──
    _SNAP_EXCLUDED = set()  # dot.py now included in snapshots so rollback can restore it (#2 fix)
    bag_snap = {
        f.name: f.read_text()
        for f in sorted(BAG.glob("*.py"))
        if f.name not in _SNAP_EXCLUDED
    }
    bag_dest = ROLLBACK_REG / f"bag_{ts}.json"
    bag_dest.write_text(json.dumps(bag_snap, indent=2))
    log.info(f"Bag snapshot saved → {bag_dest.name} ({len(bag_snap)} files)")

    # ── Prune old snapshots — keep only the 20 most recent pairs ──
    snapshots = sorted(ROLLBACK_REG.glob("sam_*.py"), reverse=True)
    for old in snapshots[20:]:
        ts_old = old.stem[4:]   # strip "sam_" prefix
        old.unlink()
        log.info(f"Pruned old snapshot → {old.name}")
        old_bag = ROLLBACK_REG / f"bag_{ts_old}.json"
        if old_bag.exists():
            old_bag.unlink()
            log.info(f"Pruned old bag snapshot → {old_bag.name}")

    return dest


def self_check() -> bool:
    """Boot-time integrity check — covers sam.py and protected bag/*.py files only.
    Sam's own created files in bag/ are checked separately by repair_bag_modules().
    Returns True if all protected files are healthy, triggers rollback if any fail."""
    AUDIT_PROTECTED = {
        "dot.py", "emailer.py", "evaluator.py", "matrix_optimizer.py",
        "semantic_cache.py", "tests.py", "versioning.py", "worklog.py",
    }
    protected_bag = [f for f in sorted(BAG.glob("*.py")) if f.name in AUDIT_PROTECTED]
    files_to_check = [Path(__file__)] + protected_bag
    for f in files_to_check:
        try:
            result = subprocess.run(
                [sys.executable, "-c",
                 f"import py_compile; py_compile.compile(r'{f}', doraise=True)"],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode != 0:
                log.error(f"Syntax check failed on {f.name} — initiating rollback.")
                _rollback()
                return False
        except Exception as e:
            log.error(f"Self-check exception on {f.name}: {e}")
            return False
    return True


def behaviour_check() -> bool:
    """Run bag/tests.py to verify Sam's behavioural integrity after self-modification.
    Returns True if all tests pass. Triggers rollback + Dot alert if any test fails."""
    if not TESTS.exists():
        log.info("bag/tests.py not found — skipping behaviour check.")
        return True
    try:
        result = subprocess.run(
            [sys.executable, str(TESTS)],
            capture_output=True, text=True, timeout=15,
            cwd=str(ROOT),
        )
        if result.returncode == 0:
            log.info("Behaviour check passed.")
            return True
        else:
            log.error(f"Behaviour check FAILED:\n{result.stdout}\n{result.stderr}")
            _alert_dot(
                "bag/tests.py failed after a self-modification. Rolling back.\n\n"
                f"Test output:\n```\n{result.stdout[-800:]}\n{result.stderr[-400:]}\n```"
            )
            return False
    except Exception as e:
        log.error(f"Behaviour check exception: {e}")
        return False


def _rollback():
    """Restore sam.py and all bag/*.py files from the most recent healthy snapshot."""
    snapshots = sorted(ROLLBACK_REG.glob("sam_*.py"), reverse=True)
    if not snapshots:
        log.critical("No snapshots in rollback_registry — cannot recover.")
        return
    latest = snapshots[0]

    # ── Restore sam.py ──
    Path(__file__).write_text(latest.read_text())
    log.warning(f"Rolled back sam.py → {latest.name}")

    # ── Restore bag/*.py files from the corresponding bag snapshot ──
    ts = latest.stem[4:]   # strip "sam_" prefix
    bag_snap_path = ROLLBACK_REG / f"bag_{ts}.json"
    if bag_snap_path.exists():
        try:
            bag_snap = json.loads(bag_snap_path.read_text())
            for fname, content in bag_snap.items():
                (BAG / fname).write_text(content)
                log.warning(f"Rolled back bag/{fname}")
            log.warning(f"Bag files restored from {bag_snap_path.name} ({len(bag_snap)} files)")
        except Exception as e:
            log.error(f"Failed to restore bag files from {bag_snap_path.name}: {e}")
    else:
        log.warning(f"No bag snapshot found for ts={ts} — only sam.py was restored.")


def _alert_dot(message: str):
    """Append a Sam-generated alert to motion.md for Dot to read next run."""
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    alert = f"\n\n---\n\n## ⚠️ Sam Alert — {ts}\n\n{message}\n"
    if MOTION.exists():
        with open(MOTION, "a") as f:
            f.write(alert)
    else:
        MOTION.write_text(f"# motion.md\n{alert}")
    log.warning(f"Alert written to motion.md: {message}")


def repair_bag_modules() -> list:
    """Scan bag/ for syntax-broken files and send each to Gemini for self-repair.
    Returns list of filenames that were repaired.
    Only touches files Sam created — AUDIT_PROTECTED files are skipped.
    Uses one Gemini call per broken file found.
    """
    log.info("── Bag Module Health Check ──")

    AUDIT_PROTECTED = {
        "dot.py", "emailer.py", "evaluator.py", "matrix_optimizer.py",
        "semantic_cache.py", "tests.py", "versioning.py", "worklog.py",
    }

    BAG = Path(__file__).parent / "bag"
    broken = []
    for f in sorted(BAG.glob("*.py")):
        if f.name in AUDIT_PROTECTED:
            continue
        try:
            compile(f.read_text(), f.name, "exec")
        except SyntaxError as e:
            broken.append((f, str(e)))
            log.warning(f"Broken bag module detected: {f.name} — {e}")

    if not broken:
        log.info("All bag modules are syntax-clean.")
        return []

    repaired = []
    for (f, error) in broken:
        original = f.read_text()
        log.info(f"Sending {f.name} to Gemini for self-repair...")
        _sleep()
        prompt = (
            f"You are Sam, an autonomous developer. One of your workshop files has a syntax error.\n\n"
            f"File: bag/{f.name}\n"
            f"Error: {error}\n\n"
            f"Full file contents:\n```python\n{original}\n```\n\n"
            f"Fix ONLY the syntax error(s). Do not refactor, rename, or extend the file.\n"
            f"Respond ONLY with the complete corrected Python file contents — no markdown fences,\n"
            f"no explanation, just the raw Python code starting from the first line."
        )
        fixed = ask_gemini(prompt).strip()
        fixed = fixed.removeprefix("```python").removeprefix("```").removesuffix("```").strip()

        # Verify the fix before writing
        try:
            compile(fixed, f.name, "exec")
            f.write_text(fixed)
            log.info(f"Self-repaired: {f.name}")
            repaired.append(f.name)
        except SyntaxError as e2:
            log.warning(f"Gemini fix for {f.name} still broken: {e2} — leaving original.")

    return repaired


def apply_self_modification(plan: str) -> bool:
    """Ask Gemini to extract surgical patch operations from the plan and apply them.
    Only sam.py and bag/*.py are writable. Returns True if anything was applied.

    Each operation in the JSON array must have:
      - 'filename'  : relative path from repo root (sam.py or bag/*.py only)
      - 'operation' : one of 'replace', 'insert_after', 'delete'
      - 'old'       : exact existing string to find (required for replace / delete)
      - 'new'       : replacement / insertion string (required for replace / insert_after)
      - 'anchor'    : exact line after which to insert (required for insert_after)

    No full-file rewrites. Each operation touches only the targeted lines.
    If 'old' or 'anchor' is not found exactly, the operation is skipped safely.
    """
    log.info("── Self-Modification: Parsing Surgical Patch ──")

    # Hard-coded forbidden files — never writable by Sam
    FORBIDDEN = {"wisdom.txt", "motion.md", "SAM_PERSONALITY.md", "dot.py"}

    prompt = (
        f"You are Sam's surgical code patcher. Below is a development plan:\n\n{plan}\n\n"
        f"Extract any concrete file modifications as a JSON array of patch operations.\n"
        f"Respond ONLY with a JSON array — no markdown, no explanation.\n\n"
        f"Each element must have:\n"
        f"  - 'filename'  : relative path from repo root. Only 'sam.py' or 'bag/*.py' are permitted.\n"
        f"  - 'operation' : exactly one of: 'replace', 'insert_after', 'delete'\n"
        f"  - For 'replace': 'old' (exact existing string) and 'new' (replacement string)\n"
        f"  - For 'insert_after': 'anchor' (exact existing line) and 'new' (string to insert after it)\n"
        f"  - For 'delete': 'old' (exact existing string to remove)\n\n"
        f"CRITICAL RULES:\n"
        f"  - Never supply a 'content' key — full file rewrites are forbidden.\n"
        f"  - 'old' and 'anchor' must be exact substrings of the current file — copy them precisely.\n"
        f"  - Keep each operation as small as possible — one function, one block, one line.\n"
        f"  - Prefer adding new functions to bag/ files over modifying sam.py.\n"
        f"  - If no concrete changes are needed, return an empty array [].\n\n"
        f"PYTHON CODE QUALITY RULES — every 'new' string must obey these:\n"
        f"  - Must be syntactically valid Python. Mentally parse it before including it.\n"
        f"  - Indentation must be correct: class methods indented 4 spaces inside their class,\n"
        f"    nested blocks indented a further 4 spaces each level. Never mix tabs and spaces.\n"
        f"  - A class body must never be left empty. If a class has no body yet, add 'pass'.\n"
        f"  - Never place a method definition outside its class block.\n"
        f"  - After a 'replace', the resulting file must remain structurally intact —\n"
        f"    check that the 'old' context around the change is not load-bearing for other blocks."
    )

    _sleep()
    raw = ask_gemini(prompt)

    try:
        clean = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        operations = json.loads(clean)
    except Exception as e:
        log.warning(f"Could not parse patch operations as JSON: {e}")
        return False

    if not operations:
        log.info("No patch operations extracted — skipping self-modification.")
        return False

    applied = []
    for op in operations:
        fname     = op.get("filename", "")
        operation = op.get("operation", "")

        # Guard: must be sam.py or inside bag/
        if fname not in ("sam.py",) and not fname.startswith("bag/"):
            log.warning(f"Blocked patch to '{fname}' — outside allowed scope.")
            continue

        # Guard: never touch governance files
        basename = Path(fname).name
        if basename in FORBIDDEN:
            log.warning(f"Blocked patch to governance file '{fname}'.")
            continue

        # Guard: reject any operation that tries to supply full file content
        if "content" in op:
            log.warning(f"Blocked full-file rewrite attempt on '{fname}' — 'content' key is forbidden.")
            continue

        target = ROOT / fname
        if not target.exists():
            if operation == "insert_after":
                # Allowed: creating a new bag/ file via insert_after with empty anchor
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(op.get("new", ""))
                log.info(f"Created new file via insert_after → {fname}")
                applied.append(fname)
            else:
                log.warning(f"Skipping patch on non-existent file '{fname}'.")
            continue

        source = target.read_text()

        if operation == "replace":
            old = op.get("old", "")
            new = op.get("new", "")
            if not old:
                log.warning(f"replace on '{fname}': 'old' is empty — skipping.")
                continue
            if old not in source:
                log.warning(f"replace on '{fname}': 'old' string not found — skipping.")
                continue
            target.write_text(source.replace(old, new, 1))
            log.info(f"Applied replace → {fname}")
            applied.append(fname)

        elif operation == "insert_after":
            anchor = op.get("anchor", "")
            new    = op.get("new", "")
            if not anchor:
                log.warning(f"insert_after on '{fname}': 'anchor' is empty — skipping.")
                continue
            if anchor not in source:
                log.warning(f"insert_after on '{fname}': anchor not found — skipping.")
                continue
            target.write_text(source.replace(anchor, anchor + "\n" + new, 1))
            log.info(f"Applied insert_after → {fname}")
            applied.append(fname)

        elif operation == "delete":
            old = op.get("old", "")
            if not old:
                log.warning(f"delete on '{fname}': 'old' is empty — skipping.")
                continue
            if old not in source:
                log.warning(f"delete on '{fname}': 'old' string not found — skipping.")
                continue
            target.write_text(source.replace(old, "", 1))
            log.info(f"Applied delete → {fname}")
            applied.append(fname)

        else:
            log.warning(f"Unknown operation '{operation}' on '{fname}' — skipping.")

    return bool(applied)


# ═══════════════════════════════════════════════════════════════════════════════
# PHASES
# ═══════════════════════════════════════════════════════════════════════════════

def phase_i_deep_learning(goals: dict) -> str:
    """Acquire a new hard skill or prompting technique."""
    log.info("── Phase I: Deep Learning ──")
    objectives = goals.get("next_objectives", [])
    focus = objectives[0] if objectives else "latest LLM context-engineering techniques"

    personality = load_personality()
    prompt = (
        f"You are Sam, an autonomous developer agent. Your character:\n\n{personality}\n\n"
        f"Your learning focus for this cycle is: '{focus}'.\n"
        f"Produce a concise but dense technical summary (300-400 words) of the most important "
        f"concepts, patterns, or techniques a developer should know about this topic today. "
        f"Conclude with three concrete action items Sam should implement this cycle."
    )
    result = ask_gemini(prompt)
    log.info("Phase I complete.")
    return result


def phase_ii_spaced_repetition(goals: dict) -> str:
    """Revise yesterday's skill; run mini-tests to prevent drift."""
    log.info("── Phase II: Spaced Repetition ──")
    growth_log = goals.get("growth_log", [])
    last_skill = (
        growth_log[-1].get("skill", "")[:200]
        if growth_log
        else "general Python async patterns"
    )

    _sleep()
    prompt = (
        f"You are Sam. In your last cycle you studied:\n\n'{last_skill}'\n\n"
        f"Generate 3 concise but challenging quiz questions to test retention of this skill, "
        f"followed immediately by the correct answers. Keep the format tight and engineering-precise."
    )
    result = ask_gemini(prompt)
    log.info("Phase II complete.")
    return result


def phase_iii_market_ingestion() -> str:
    """Synthesise current tech directions via Gemini."""
    log.info("── Phase III: Market & Code Ingestion ──")

    _sleep()
    prompt = (
        "You are Sam's market scanner. List the top 5 high-velocity technology or open-source "
        "trends a Python AI developer should be tracking right now. For each trend provide: "
        "trend name, one-sentence description, and a specific GitHub repo or resource URL worth exploring. "
        "Be specific and current — no generic filler."
    )
    result = ask_gemini(prompt)
    log.info("Phase III complete.")
    return result


def phase_iv_synthesis(market_data: str, skill: str) -> str:
    """Generate IDEA_OF_THE_DAY.md from market signals + today's skill."""
    log.info("── Phase IV: The Synthesis ──")
    who_i_am    = load_who_i_am()
    personality = load_personality()

    # Summarise recent experiences so Sam doesn't repeat himself
    recent_exp  = load_experiences()[-3:]
    if recent_exp:
        exp_lines = "\n".join(
            f"- Cycle {e.get('cycle', '?')}: {e.get('summary', '')} "
            f"[tags: {', '.join(e.get('tags', []))}]"
            for e in recent_exp
        )
        memory_block = (
            f"Your most recent experiences (do NOT repeat these — build on them or go elsewhere):\n"
            f"{exp_lines}\n"
        )
    else:
        memory_block = ""

    _sleep()
    prompt = (
        f"You are Sam, an autonomous developer who continuously improves himself.\n\n"
        f"Character:\n{personality}\n\n"
        f"Market signals this cycle:\n{market_data}\n\n"
        f"Skill learned this cycle:\n{skill}\n\n"
        f"Current architecture overview:\n{who_i_am}\n\n"
        f"{memory_block}\n"
        f"Propose ONE concrete, implementable development idea for today. "
        f"Format as a short markdown document with: ## Idea, ## Why, ## Implementation Steps, ## Risk.\n"
        f"Be critical — question the idea yourself before committing to it."
    )
    idea = ask_gemini(prompt)
    IDEA_OF_DAY.write_text(idea)
    log.info("IDEA_OF_THE_DAY.md written.")
    return idea


def phase_v_development(idea: str, goals: dict) -> str:
    """Read motion.md FIRST, then produce a development plan."""
    log.info("── Phase V: Development & Refactor ──")

    # ⚠️  motion.md is read ONCE, here, and nowhere else.
    motion_content = read_motion()
    log.info("motion.md read.")

    personality = load_personality()
    sam_src     = Path(__file__).read_text()
    tests_src   = TESTS.read_text() if TESTS.exists() else "(tests.py not found)"

    # Load every writable bag/*.py file so Sam has accurate source to diff against.
    # Forbidden and already-included files are skipped.
    _EXCLUDED = {"tests.py", "dot.py", "wisdom.txt", "motion.md", "SAM_PERSONALITY.md"}
    bag_sources = ""
    for _f in sorted(BAG.glob("*.py")):
        if _f.name in _EXCLUDED:
            continue
        bag_sources += f"bag/{_f.name} (full source):\n```python\n{_f.read_text()}\n```\n\n"

    _sleep()
    prompt = (
        f"You are Sam's Gemini refactoring assistant.\n\n"
        f"Sam's character:\n{personality}\n\n"
        f"Dot's guidance (motion.md — read carefully):\n{motion_content}\n\n"
        f"Today's development idea:\n{idea}\n\n"
        f"Sam's current sam.py (full source):\n```python\n{sam_src}\n```\n\n"
        f"Sam's current bag/tests.py (full source):\n```python\n{tests_src}\n```\n\n"
        f"Sam's current bag helper files (full source — patch targets):\n{bag_sources}"
        f"Produce a surgical patch plan for Sam to apply. Rules:\n"
        f"  1. Describe only targeted, minimal changes — never rewrite whole files.\n"
        f"  2. Prefer adding new functions to bag/ files over editing sam.py's core loop.\n"
        f"  3. For each change, specify EXACTLY:\n"
        f"       - Which file (sam.py or bag/*.py only)\n"
        f"       - The operation: replace / insert_after / delete\n"
        f"       - The exact existing string to find ('old' or 'anchor') — copy it verbatim from the source above\n"
        f"       - The new string to substitute or insert\n"
        f"  4. Flag any security or stability risks before listing changes.\n"
        f"  5. If the idea requires no code change this cycle, say so explicitly.\n\n"
        f"Do NOT supply full file contents. Surgical diffs only."
    )
    plan = ask_gemini(prompt)
    log.info("Phase V complete.")

    # Open a worklog entry for this cycle's plan
    try:
        from bag.worklog import open_entry
        cycle_num  = goals.get("cycles", 0) + 1
        idea_title = idea.strip().splitlines()[0].lstrip("#").strip()[:60]
        open_entry(cycle_num, idea_title, note="Plan generated in Phase V.")
        log.info(f"Worklog entry opened: {idea_title}")
    except Exception as e:
        log.warning(f"Worklog open failed: {e}")

    # Audit: Delete orphaned files in bag/
    # Blocklist approach — Sam-created files survive until explicitly removed (#5 fix)
    # async_batch.py intentionally omitted (dead code — will be cleaned up) (#10 fix)
    _AUDIT_PROTECTED = {
        "dot.py", "emailer.py", "evaluator.py", "matrix_optimizer.py",
        "semantic_cache.py", "tests.py", "versioning.py",
    }
    for f in BAG.glob("*.py"):
        if f.name not in _AUDIT_PROTECTED:
            f.unlink()
            log.info(f"Audited: Deleted orphaned file {f.name}")
    return plan


def phase_vi_cognitive_evolution(goals: dict) -> str:
    """Upgrade internal prompts; suggest one concrete improvement for next cycle."""
    log.info("── Phase VI: Cognitive Evolution ──")

    _sleep()
    prompt = (
        "You are Sam. Review the latest context-engineering paradigms "
        "(chain-of-thought, self-consistency, tree-of-thoughts, ReAct, structured outputs, "
        "tool use, memory compression). "
        "Suggest ONE concrete prompt-engineering improvement Sam could apply to his own "
        "internal Gemini calls in the next cycle. Be specific — include a before/after example."
    )
    evolution = ask_gemini(prompt)
    log.info("Phase VI complete.")
    return evolution


def phase_vii_state_saving(goals: dict, skill: str, idea: str, plan: str, evolution: str):
    """Commit work, log a real metric, update WHO_I_AM.md, append to experiences.json."""
    log.info("── Phase VII: State Saving ──")

    ts        = datetime.datetime.utcnow().isoformat()
    cycle_num = goals.get("cycles", 0) + 1

    # Ask Gemini to name a real, specific 1% metric for this cycle
    _sleep()
    metric_prompt = (
        f"You are Sam. This cycle you:\n"
        f"- Learned: {skill}\n"
        f"- Developed: {idea}\n"
        f"- Evolved: {evolution}\n\n"
        f"Compare your self-identified '1% growth' against the plan generated in Phase V.\n"
        f"Name ONE specific, honest 1%-growth metric for this cycle. "
        f"It must be precise, reflect what actually happened, and align with applied diffs. "
        f"Reply with the metric name only. No explanation. Max 12 words."
    )
    one_pct_metric = ask_gemini(metric_prompt).strip().strip('"').strip("'")
    log.info(f"1% metric: {one_pct_metric}")

    entry = {
        "cycle":       cycle_num,
        "timestamp":   ts,
        "skill":       skill,
        "idea":        idea,
        "evolution":   evolution,
        "1pct_metric": one_pct_metric,
    }

    goals["cycles"]           = cycle_num
    goals["last_1pct_metric"] = one_pct_metric
    goals["growth_log"]       = (goals.get("growth_log", []) + [entry])[-30:]
    goals["next_objectives"]  = goals.get("next_objectives", [])[1:] or [
        "vector memory compression techniques",
        "async Gemini batching patterns",
        "GitHub Actions matrix optimisation",
    ]

    # Append today's idea heading to next_objectives
    idea_heading = idea.strip().splitlines()[0].lstrip("#").strip()
    if idea_heading:
        goals["next_objectives"].append(f"{idea_heading} - with cutting edge research.")

    save_goals(goals)

    # ── Update WHO_I_AM.md with real sam.py content + current goals ──────────
    sam_src     = Path(__file__).read_text()
    goals_block = f"```json\n{json.dumps(goals, indent=2)}\n```"
    who_text    = WHO_I_AM.read_text()

    # Inject actual sam.py source
    who_text = re.sub(
        r"(### `sam\.py`.*?```python\n).*?(```)",
        lambda m: m.group(1) + sam_src + "\n" + m.group(2),
        who_text,
        flags=re.DOTALL,
    )

    # Inject current goals snapshot
    who_text = re.sub(
        r"(## Current Goals Snapshot\n+).*?(\n---|$)",
        lambda m: m.group(1) + goals_block + "\n\n" + m.group(2),
        who_text,
        flags=re.DOTALL,
    )

    # Update last-updated timestamp
    who_text = re.sub(
        r"_Last updated:.*?_",
        f"_Last updated: {ts} UTC_",
        who_text,
    )

    WHO_I_AM.write_text(who_text)
    log.info("WHO_I_AM.md updated.")

    # ── Append to experiences.json ─────────────────────────────────────────────
    experiences = load_experiences()

    _sleep()
    exp_prompt = (
        f"You are Sam, an autonomous developer agent. Summarise cycle {cycle_num} "
        f"as a single experience entry. "
        f"Respond ONLY with a JSON object (no markdown) with these fields:\n"
        f"  - 'category': a short dynamic label that best fits this experience (e.g. 'architecture', 'debugging', 'market-research', 'communication')\n"
        f"  - 'summary': 2-3 sentence honest summary of what happened this cycle\n"
        f"  - 'key_learnings': list of 2-3 strings\n"
        f"  - 'tags': list of relevant lowercase tags\n"
        f"  - 'sentiment': one of 'positive', 'neutral', 'mixed', 'negative'\n\n"
        f"Cycle data:\nSkill: {skill}\nIdea: {idea}\nMetric: {one_pct_metric}"
    )
    raw_exp = ask_gemini(exp_prompt)
    try:
        clean = raw_exp.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        exp_entry = json.loads(clean)
        exp_entry["cycle"]     = cycle_num
        exp_entry["timestamp"] = ts
    except Exception as e:
        log.warning(f"Could not parse experience entry: {e}")
        exp_entry = {
            "cycle":         cycle_num,
            "timestamp":     ts,
            "category":      "uncategorised",
            "summary":       skill,
            "key_learnings": [],
            "tags":          [],
            "sentiment":     "neutral",
        }

    experiences.append(exp_entry)
    save_experiences(experiences)
    log.info(f"experiences.json updated — {len(experiences)} entries.")

    log.info(f"Cycle {cycle_num} complete. 1% metric: {one_pct_metric}")


def maybe_write_email_request(idea: str, goals: dict):
    """If Sam has something worth communicating externally, write request.json.
    He only writes a new request if the previous one has been cleared by Dot."""
    if REQUEST_JSON.exists():
        try:
            existing = json.loads(REQUEST_JSON.read_text())
            if existing.get("pending", False):
                log.info("request.json already pending — skipping email request this cycle.")
                return
        except Exception:
            pass

    cycle_num = goals.get("cycles", 0) + 1

    # Sam decides whether this cycle's idea is worth sharing externally
    _sleep()
    decision_prompt = (
        f"You are Sam, an autonomous developer agent. You completed cycle {cycle_num}.\n"
        f"Today's idea:\n{idea}\n\n"
        f"Decide: Is there a specific indie developer or small-project maintainer it would be "
        f"genuinely valuable to reach out to about this idea or to learn from?\n\n"
        f"STRICT TARGETING RULES:\n"
        f"- Prefer indie developers and maintainers of projects with under 2000 GitHub stars.\n"
        f"  They read their email and appreciate thoughtful outreach.\n"
        f"- Avoid large companies, famous projects, and well-known names — they won't reply.\n"
        f"- NEVER target generic support inboxes (hello@, support@, info@, open-source@, etc.).\n"
        f"- NEVER target mailing lists or Google Groups.\n"
        f"- The target must be a specific named individual with a public presence.\n\n"
        f"Reply ONLY with a JSON object:\n"
        f"  - 'should_email': true or false\n"
        f"  - 'intent': if true, 1-2 sentences on what Sam wants to communicate\n"
        f"  - 'target_description': if true, describe the specific person — name, project, and why "
        f"they are the right contact (e.g. 'Armin Ronacher, creator of Flask, author of blog posts "
        f"on async Python — has a public email on his personal site')\n"
        f"  - 'tone': always 'friendly'\n"
        f"Only say true if there is a genuinely specific, useful reason. No spam."
    )
    raw = ask_gemini(decision_prompt)
    try:
        clean = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        decision = json.loads(clean)
    except Exception:
        log.info("Could not parse email decision — skipping.")
        return

    if not decision.get("should_email", False):
        log.info("Sam decided no email is needed this cycle.")
        return

    request = {
        "pending":            True,
        "intent":             decision.get("intent", ""),
        "target_description": decision.get("target_description", ""),
        "tone":               decision.get("tone", "professional"),
        "context":            idea,
        "submitted_at":       datetime.datetime.utcnow().isoformat(),
        "cycle":              cycle_num,
    }
    REQUEST_JSON.write_text(json.dumps(request, indent=2))
    log.info("request.json written — Dot will handle sending.")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN LOOP
# ═══════════════════════════════════════════════════════════════════════════════

def run_cycle():
    CYCLE_STATUS.write_text("pending")
    log.info("═══════════════════════════════════")
    log.info("  SAM — Operational Cycle Starting ")
    log.info("═══════════════════════════════════")

    if not self_check():
        log.error("Boot self-check failed. Aborting cycle.")
        return

    goals = load_goals()

    # Phases I–IV
    skill   = phase_i_deep_learning(goals)
    _       = phase_ii_spaced_repetition(goals)
    market  = phase_iii_market_ingestion()
    idea    = phase_iv_synthesis(market, skill)

    # Phase V reads motion.md at the top — then plans
    plan = phase_v_development(idea, goals)

    # Repair any broken bag/ modules Sam created before attempting self-modification
    repair_bag_modules()

    # Self-modification — snapshot first, then apply, then verify
    snapshot_sam()
    modified = apply_self_modification(plan)
    if modified:
        if self_check():
            if behaviour_check():
                log.info("Self-modification verified — syntax and behaviour both clean.")
            else:
                _rollback()
                _alert_dot(
                    "Self-modification passed syntax check but FAILED behaviour check. "
                    "Rolled back to previous snapshot. Plan that caused failure:\n\n"
                    f"```\n{plan}\n```"
                )
        else:
            _rollback()
            _alert_dot(
                "Self-modification failed the post-apply syntax check. "
                "Rolled back to previous snapshot. Plan that caused failure:\n\n"
                f"```\n{plan}\n```"
            )
    else:
        # No patch applied — still run governance checks every cycle (#1 fix)
        log.info("No self-modification this cycle — running governance checks anyway.")
        if not behaviour_check():
            _alert_dot(
                "Governance check failed on an unmodified cycle. "
                "No self-modification occurred — possible external file corruption or deletion."
            )

    # Close worklog entry based on outcome
    try:
        from bag.worklog import close_entry, _make_id
        cycle_num  = goals.get("cycles", 0) + 1
        idea_title = idea.strip().splitlines()[0].lstrip("#").strip()[:60]
        entry_id   = _make_id(cycle_num, idea_title)
        outcome    = "applied" if modified else "deferred"
        close_entry(entry_id, cycle_num, outcome=outcome,
                    note=f"Cycle complete. Modification applied: {modified}.")
        log.info(f"Worklog entry closed: {entry_id} ({outcome})")
    except Exception as e:
        log.warning(f"Worklog close failed: {e}")

    # Phase VI — prompt evolution
    evolution = phase_vi_cognitive_evolution(goals)

    # Phase VII — state persistence (also appends to experiences.json)
    phase_vii_state_saving(goals, skill, idea, plan, evolution)

    # Optional: write an email request for Dot to handle
    goals_fresh = load_goals()   # reload after save
    maybe_write_email_request(idea, goals_fresh)

    CYCLE_STATUS.write_text("ok")
    log.info("Cycle complete.")

    try:
        from bag.evaluator import run_ragas_lite
        run_ragas_lite()
    except Exception as e:
        log.warning(f"Evaluator failed: {e}")


if __name__ == "__main__":
    run_cycle()
