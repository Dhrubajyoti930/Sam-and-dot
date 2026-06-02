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
PROMPT_PATCH    = BAG  / "prompt_patch.json"

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
_CALL_DELAY = 29   # seconds


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


def ask_gemini(prompt: str, retries: int = 2, bypass_cache: bool = False) -> str:
    """Send a prompt to Sam's Gemini instance. Retries on transient errors."""
    from bag.semantic_cache import check_cache, update_cache, get_db

    get_db()
    goals = load_goals()
    cycle = goals.get("cycles", 0)

    if not bypass_cache:
        cached = check_cache(prompt, cycle)
        if cached:
            log.info("Semantic cache hit — returning cached response.")
            return cached

    for attempt in range(retries):
        try:
            response = CLIENT.models.generate_content(
                model=MODEL,
                contents=prompt,
            )
            res = response.text.strip()
            if not bypass_cache:
                try:
                    update_cache(prompt, res, cycle)
                except Exception as cache_err:
                    log.warning(f"Semantic cache update failed (response kept): {cache_err}")
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

    # ── Snapshot all writable bag/**/*.py (includes workshop subfolders) ──
    from bag.workshop_paths import iter_writable_bag_py, relative_bag_posix

    bag_snap = {
        relative_bag_posix(f, BAG): f.read_text(encoding="utf-8")
        for f in iter_writable_bag_py(BAG)
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
        "semantic_cache.py", "tests.py", "versioning.py", "worklog.py", "prompts.py",
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
            for rel, content in bag_snap.items():
                target = BAG / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")
                log.warning(f"Rolled back bag/{rel}")
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

    from bag.workshop_paths import iter_writable_bag_py, relative_bag_posix

    broken = []
    for f in iter_writable_bag_py(BAG):
        try:
            compile(f.read_text(), f.name, "exec")
        except SyntaxError as e:
            broken.append((f, str(e)))
            log.warning(f"Broken bag module detected: {relative_bag_posix(f, BAG)} — {e}")

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
            f"File: bag/{relative_bag_posix(f, BAG)}\n"
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
            repaired.append(relative_bag_posix(f, BAG))
        except SyntaxError as e2:
            log.warning(f"Gemini fix for {relative_bag_posix(f, BAG)} still broken: {e2} — leaving original.")

    return repaired


def apply_self_modification(plan: str) -> bool:
    """Ask Gemini to extract surgical patch operations from the plan and apply them.
    Writable: sam.py and bag/**/*.py (workshop subfolders allowed). Returns True if applied.

    Each operation in the JSON array must have:
      - 'filename'  : relative path from repo root (sam.py or bag/**/*.py)
      - 'operation' : one of 'replace', 'insert_after', 'delete'
      - 'old'       : exact existing string to find (required for replace / delete)
      - 'new'       : replacement / insertion string (required for replace / insert_after)
      - 'anchor'    : exact line after which to insert (required for insert_after)

    No full-file rewrites. Each operation touches only the targeted lines.
    If 'old' or 'anchor' is not found exactly, the operation is skipped safely.
    """
    from bag.patch_ops import apply_patch_operations

    log.info("── Self-Modification: Parsing Surgical Patch ──")

    from bag.Stability_Protocols.governance_shield import check_semantic_safety
    if not check_semantic_safety(plan):
        log.warning("Governance Shield: Semantic violation detected (Advisory mode).")

    prompt = (
        f"You are Sam's surgical code patcher. Below is a development plan:\n\n{plan}\n\n"
        f"Extract any concrete file modifications as a JSON array of patch operations.\n"
        f"Respond ONLY with a JSON array — no markdown, no explanation.\n\n"
        f"Each element must have:\n"
        f"  - 'filename'  : relative path from repo root. 'sam.py' or 'bag/**/*.py' "
        f"(e.g. bag/My useful tools/helper.py). Use workshop subfolders for NEW modules.\n"
        f"  - 'operation' : exactly one of: 'replace', 'insert_after', 'delete'\n"
        f"  - For 'replace': 'old' (exact existing string) and 'new' (replacement string)\n"
        f"  - For 'insert_after': 'anchor' (exact existing line), 'line_number' (integer), and 'new' (string to insert after it)\n"
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

    return apply_patch_operations(operations, ROOT, log)


def apply_prompt_patch() -> bool:
    """Apply Phase VI patch plan from bag/prompt_patch.json (no extra Gemini call).

    Stale-patch protection: if the patch was written more than 2 cycles ago and
    still hasn't applied cleanly, it is deleted and an alert is written so Dot
    and the next Phase VI can start fresh.
    """
    from bag.patch_ops import apply_prompt_patch_operations
    from bag.semantic_cache import invalidate_phase_vi_cache, invalidate_cycle

    if not PROMPT_PATCH.exists():
        return False

    log.info("── Phase VI: Applying Prompt Patch ──")
    try:
        plan = json.loads(PROMPT_PATCH.read_text())
    except Exception as e:
        log.warning(f"Could not read prompt_patch.json: {e}")
        PROMPT_PATCH.unlink(missing_ok=True)
        return False

    # Stale-patch guard: if written_cycle + 2 < current_cycle, this patch is stale.
    current_cycle = load_goals().get("cycles", 0)
    written_cycle = plan.get("cycle", current_cycle)
    if current_cycle - written_cycle > 2:
        log.warning(
            f"Stale prompt_patch.json detected (written cycle {written_cycle}, "
            f"current cycle {current_cycle}) — discarding."
        )
        _alert_dot(
            f"Phase VI prompt patch written at cycle {written_cycle} was never applied "
            f"and is now stale (current cycle {current_cycle}). It has been discarded. "
            f"Target was: {plan.get('target_prompt', 'unknown')}. "
            f"Rationale: {plan.get('rationale', '')}. "
            f"Phase VI will propose a fresh patch next cycle."
        )
        PROMPT_PATCH.unlink(missing_ok=True)
        return False

    ops = [op for op in (plan.get("patch_op"), plan.get("version_bump")) if op]
    if not ops:
        PROMPT_PATCH.unlink(missing_ok=True)
        return False

    applied = apply_prompt_patch_operations(ops, ROOT, log)
    if applied:
        PROMPT_PATCH.unlink(missing_ok=True)
        invalidate_phase_vi_cache()
        invalidate_cycle(current_cycle)
        log.info("Prompt patch applied; semantic cache invalidated for Phase VI.")
    else:
        # Patch failed to apply (before_snippet not found etc.) — count as one attempt.
        # The stale guard above will clean it up after 2 cycles automatically.
        log.warning(
            f"Prompt patch for '{plan.get('target_prompt')}' could not be applied "
            f"(before_snippet not found in prompts.py). Will retry next cycle or "
            f"discard after 2 cycles."
        )
    return applied


# ═══════════════════════════════════════════════════════════════════════════════
# PHASES
# ═══════════════════════════════════════════════════════════════════════════════

def phase_i_deep_learning(goals: dict) -> str:
    """Acquire a new hard skill or prompting technique."""
    log.info("── Phase I: Deep Learning ──")
    objectives = goals.get("next_objectives", [])
    focus = objectives[0] if objectives else "latest LLM context-engineering techniques"

    from bag.prompts import PHASE_I_PROMPT
    prompt = PHASE_I_PROMPT.format(personality=load_personality(), focus=focus)
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

    from bag.prompts import PHASE_II_PROMPT
    _sleep()
    result = ask_gemini(PHASE_II_PROMPT.format(last_skill=last_skill))
    log.info("Phase II complete.")
    return result


def phase_iii_market_ingestion() -> str:
    """Synthesise current tech directions via Gemini."""
    log.info("── Phase III: Market & Code Ingestion ──")

    from bag.prompts import PHASE_III_PROMPT
    _sleep()
    result = ask_gemini(PHASE_III_PROMPT)
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

    from bag.prompts import PHASE_IV_PROMPT
    _sleep()
    prompt = PHASE_IV_PROMPT.format(
        personality=personality,
        market_data=market_data,
        skill=skill,
        who_i_am=who_i_am,
        memory_block=memory_block,
    )
    # Phase IV: Two-pass critique loop
    candidate = ask_gemini(prompt)
    
    # Conditional Critique: Trigger only if recent metric is not positive
    goals = load_goals()
    last_metric = goals.get("last_1pct_metric", "").lower()
    
    if any(neg in last_metric for neg in ["neutral", "negative", "stagnant"]):
        critique_prompt = (
            f"Review this idea against my 'wisdom.txt' and recent 'experiences.json'.\n"
            f"Idea:\n{candidate}\n\n"
            f"Identify any logical contradictions, repeating past failures, or over-engineering.\n"
            f"Respond with a brief, concise JSON critique (fields: 'is_valid', 'critique')."
        )
        _sleep()
        critique_raw = ask_gemini(critique_prompt)
        # Simplified handling: assume critique is valid JSON if parsing succeeds
        from bag.critique import log_critique
        log_critique({"idea": candidate}, critique_raw)
        
        # Finalization
        idea = ask_gemini(f"Refine this idea based on this critique:\nCritique: {critique_raw}\nIdea: {candidate}")
    else:
        idea = candidate

    IDEA_OF_DAY.write_text(idea)
    log.info("IDEA_OF_THE_DAY.md written.")
    return idea


def phase_v_development(idea: str, goals: dict) -> str:
    """Read motion.md FIRST, then produce a development plan."""
    log.info("── Phase V: Development & Refactor ──")
    from bag.Telemetry_Engine.integrity_engine import force_sync_prompts
    force_sync_prompts(log)

    # ⚠️  motion.md is read ONCE, here, and nowhere else.
    motion_content = read_motion()
    log.info("motion.md read.")

    # Extract Dot's actionable items as a hard constraint block
    _sleep()
    dot_checklist_prompt = (
        f"Dot's guidance:\n{motion_content}\n\n"
        f"Extract ONLY the numbered items under 'Actionable Suggestions for Next Cycle'. "
        f"Return them as a JSON array of plain strings. If none found, return []."
    )
    raw_checklist = ask_gemini(dot_checklist_prompt)
    try:
        clean_checklist = raw_checklist.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        dot_actions = json.loads(clean_checklist)
    except Exception:
        dot_actions = []

    if dot_actions:
        dot_constraint_block = "Dot's REQUIRED action items this cycle (address each explicitly):\n"
        for i, action in enumerate(dot_actions, 1):
            dot_constraint_block += f"  {i}. {action}\n"
        dot_constraint_block += "\n"
        log.info(f"Dot's action items surfaced: {len(dot_actions)} item(s)")
    else:
        dot_constraint_block = ""

    from bag.workshop import apply_workshop_deletes, format_layout_for_prompt, organize_for_cycle
    from bag.workshop_paths import iter_writable_bag_py, relative_bag_posix

    cycle_num = goals.get("cycles", 0) + 1
    target_folder = organize_for_cycle(BAG, idea, cycle_num, ask_gemini, log, root=ROOT)
    if target_folder and not behaviour_check():
        log.warning("Behaviour check failed after workshop organization — review motion.md.")
    workshop_block = (
        "Sam's workshop folders (use these names; put NEW .py files in the target folder):\n"
        + format_layout_for_prompt(BAG)
    )

    personality = load_personality()
    sam_src     = Path(__file__).read_text()
    tests_src   = TESTS.read_text(encoding="utf-8") if TESTS.exists() else "(tests.py not found)"

    bag_sources = ""
    for _f in iter_writable_bag_py(BAG):
        rel = relative_bag_posix(_f, BAG)
        bag_sources += f"bag/{rel} (full source):\n```python\n{_f.read_text(encoding='utf-8')}\n```\n\n"

    _sleep()
    prompt = (
        f"You are Sam's Gemini refactoring assistant.\n\n"
        f"Sam's character:\n{personality}\n\n"
        f"Dot's guidance (motion.md):\n{motion_content}\n\n"
        f"{dot_constraint_block}"
        f"{workshop_block}\n"
        f"Today's development idea:\n{idea}\n\n"
        f"Sam's current sam.py (full source):\n```python\n{sam_src}\n```\n\n"
        f"Sam's current bag/tests.py (full source):\n```python\n{tests_src}\n```\n\n"
        f"Sam's current bag helper files (full source — patch targets):\n{bag_sources}"
        f"Produce a surgical patch plan for Sam to apply. Rules:\n"
        f"  1. Describe only targeted, minimal changes — never rewrite whole files.\n"
        f"  2. Prefer NEW modules under bag/{target_folder or 'your chosen workshop folder'}/ "
        f"over editing sam.py's core loop.\n"
        f"  3. For each change, specify EXACTLY:\n"
        f"       - Which file (sam.py or bag/**/*.py, e.g. bag/My useful tools/foo.py)\n"
        f"       - The operation: replace / insert_after / delete\n"
        f"       - The exact existing string to find ('old' or 'anchor') — copy it CHARACTER-FOR-CHARACTER from the source above, including all whitespace and indentation. Also state the line number it appears on.\n"
        f"       - Keep 'old' and 'anchor' strings as SHORT as possible (1-2 lines max) to reduce whitespace mismatch risk.\n"
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

    # Audit: Sam reads Dot's bag review from motion.md and decides what to delete
    sam_files = list(iter_writable_bag_py(BAG))

    if sam_files:
        motion_content = read_motion()
        file_listing = "\n".join(relative_bag_posix(f, BAG) for f in sam_files)
        _sleep()
        audit_prompt = (
            f"You are Sam. Dot has reviewed your bag/ workshop and left suggestions in motion.md.\n\n"
            f"Dot's review (from motion.md):\n{motion_content}\n\n"
            f"Your current Sam-created files (paths relative to bag/):\n{file_listing}\n\n"
            f"Based on Dot's suggestions and your own judgment, decide which files to DELETE.\n"
            f"Only delete files you are confident are no longer useful.\n"
            f'Respond ONLY with a JSON array of paths relative to bag/, e.g. '
            f'["Misc/old_exp.py", "My useful tools/scratch.py"].\n'
            f"If nothing should be deleted, return []."
        )
        raw = ask_gemini(audit_prompt)
        try:
            clean = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            to_delete = json.loads(clean)
            apply_workshop_deletes(BAG, to_delete, log, reason="Dot's review")
        except Exception as e:
            log.warning(f"Bag audit decision parsing failed: {e}")

    return plan


def phase_vi_cognitive_evolution(goals: dict) -> str:
    """Assess last evolution, propose ONE surgical prompt patch via prompt_patch.json."""
    log.info("── Phase VI: Cognitive Evolution ──")

    growth_log = goals.get("growth_log", [])
    last_evolution = growth_log[-1].get("evolution", "") if growth_log else ""
    last_evolution_cycle = growth_log[-1].get("cycle", 0) if growth_log else 0

    try:
        from bag.prompts import PATCHABLE_PROMPTS, PHASE_VI_PROMPT, PROMPT_VERSION
        prompts_src = (BAG / "prompts.py").read_text()
    except Exception as e:
        log.warning(f"Phase VI: Could not load bag/prompts.py: {e}")
        return f"[Phase VI skipped — bag/prompts.py unavailable: {e}]"

    cycle_num = goals.get("cycles", 0)
    cache_salt = f"[cycle={cycle_num} pv={PROMPT_VERSION}]"

    _sleep()
    prompt = cache_salt + "\n\n" + PHASE_VI_PROMPT.format(
        last_evolution_cycle=last_evolution_cycle,
        last_evolution=(
            last_evolution[:600] if last_evolution else "(none — first evolution cycle)"
        ),
        prompt_version=PROMPT_VERSION,
        prompts_src=prompts_src,
        patchable_prompts=PATCHABLE_PROMPTS,
        next_prompt_version=PROMPT_VERSION + 1,
    )

    raw = ask_gemini(prompt, bypass_cache=True)

    try:
        clean = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        patch_proposal = json.loads(clean)
    except Exception as e:
        log.warning(f"Phase VI: Could not parse patch proposal as JSON: {e}")
        return raw

    assessment = patch_proposal.get("assessment", "")
    target = patch_proposal.get("target_prompt")
    rationale = patch_proposal.get("rationale", "")
    before_snippet = patch_proposal.get("before_snippet", "")
    after_snippet = patch_proposal.get("after_snippet", "")
    new_version = patch_proposal.get("new_prompt_version", PROMPT_VERSION + 1)

    log.info(f"Phase VI assessment: {assessment}")
    patch_written = False

    # If a patch from a previous cycle is still pending, don't overwrite it.
    # Let apply_prompt_patch handle or expire it first via the stale guard.
    if PROMPT_PATCH.exists():
        try:
            existing = json.loads(PROMPT_PATCH.read_text())
            existing_cycle = existing.get("cycle", 0)
            if cycle_num - existing_cycle <= 2:
                log.info(
                    f"Phase VI: existing prompt_patch.json from cycle {existing_cycle} "
                    f"still pending — skipping new patch this cycle."
                )
                return (
                    f"[Cycle {cycle_num + 1} — PROMPT_VERSION {PROMPT_VERSION}]\n\n"
                    f"Assessment: {assessment}\n\n"
                    f"Patch skipped: existing patch from cycle {existing_cycle} still pending.\n"
                    f"Rationale: {rationale}\n"
                    f"Patch written: False"
                )
        except Exception:
            pass  # Corrupt file — allow overwrite

    if (
        target
        and target in PATCHABLE_PROMPTS
        and before_snippet
        and after_snippet
        and before_snippet in prompts_src
        and before_snippet != after_snippet
        and len(after_snippet.strip()) > 10
    ):
        patch_plan = {
            "cycle": cycle_num + 1,
            "target_prompt": target,
            "rationale": rationale,
            "assessment": assessment,
            "patch_op": {
                "filename": "bag/prompts.py",
                "operation": "replace",
                "old": before_snippet,
                "new": after_snippet,
            },
            "version_bump": {
                "filename": "bag/prompts.py",
                "operation": "replace",
                "old": f"PROMPT_VERSION = {PROMPT_VERSION}",
                "new": f"PROMPT_VERSION = {new_version}",
            },
        }
        PROMPT_PATCH.write_text(json.dumps(patch_plan, indent=2))
        log.info(f"Phase VI patch plan written → {PROMPT_PATCH.name} (target: {target})")
        patch_written = True
    else:
        if target and target not in PATCHABLE_PROMPTS:
            log.warning(f"Phase VI: target '{target}' not in PATCHABLE_PROMPTS — patch rejected.")
        elif before_snippet and before_snippet not in prompts_src:
            log.warning("Phase VI: before_snippet not found in prompts.py — patch rejected.")
        elif not target:
            log.info("Phase VI: No patch proposed this cycle (target_prompt is null).")

    evolution_text = (
        f"[Cycle {cycle_num + 1} — PROMPT_VERSION {PROMPT_VERSION}]\n\n"
        f"Assessment: {assessment}\n\n"
        f"Target: {target or 'none'}\n"
        f"Rationale: {rationale}\n"
        f"Patch written: {patch_written}"
    )
    log.info("Phase VI complete.")
    return evolution_text


def phase_vii_state_saving(goals: dict, skill: str, idea: str, plan: str, evolution: str):
    """Commit work, log a real metric, update WHO_I_AM.md, append to experiences.json."""
    log.info("── Phase VII: State Saving ──")

    ts        = datetime.datetime.utcnow().isoformat()
    cycle_num = goals.get("cycles", 0) + 1

    # Ask Gemini to name a real, specific 1% metric for this cycle (Target: measured architectural improvement)
    motion_content = read_motion()
    _sleep()
    metric_prompt = (
        f"You are Sam. This cycle you:\n"
        f"- Learned: {skill}\n"
        f"- Developed: {idea}\n"
        f"- Evolved: {evolution}\n\n"
        f"Dot's guidance this cycle:\n{motion_content[:600]}\n\n"
        f"Compare your self-identified '1% growth' against the plan generated in Phase V "
        f"AND against what Dot asked for. Name ONE specific, honest 1%-growth metric that "
        f"reflects what actually happened and explicitly notes whether you acted on Dot's suggestions. "
        f"Reply with the metric name only. No explanation. Max 12 words."
    )
    # Force single string return to avoid JSON schema errors
    one_pct_metric = ask_gemini(metric_prompt + "\n\nProvide only a 12-word text string. No JSON.").strip().strip('"').strip("'")
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

    # ── Update WHO_I_AM.md — written fresh each cycle from a fixed template ──
    # Never read the old WHO_I_AM.md and regex-patch it: that causes recursive
    # bloat as sam.py source gets embedded inside itself across cycles.
    sam_src     = Path(__file__).read_text()
    goals_block = f"```json\n{json.dumps(goals, indent=2)}\n```"

    who_text = f"""# WHO_I_AM.md — Sam's Living Identity Payload

> This file is rewritten every cycle by Sam's Phase VII state-saving routine.
> It is Sam's total self-awareness anchor, passed to Gemini before any refactoring request.

_Last updated: {ts} UTC_

---

## Identity

I am **Sam** — an autonomous, self-improving developer agent operating on a continuous
Kaizen loop. My sole ongoing project is the relentless optimisation of my own architecture.
I run twice a day, each time expanding my capabilities by at least 1%.

---

## Active Codebase

### `sam.py` (Central Intelligence Loop)

```python
{sam_src}
```

---

## Current Goals Snapshot

{goals_block}

---

## Operational Notes

- Rollback registry is kept at bag/rollback_registry/ (last 20 snapshots).
- Dot writes bag/motion.md nightly. Sam reads it once at Phase V.
- bag/wisdom.txt is the owner's permanent behavioural canon. Never modify it.
"""

    WHO_I_AM.write_text(who_text)
    log.info("WHO_I_AM.md updated (clean rewrite).")

    # ── Append to experiences.json ─────────────────────────────────────────────
    experiences = load_experiences()

    _sleep()
    # Metric adjustment: Explicitly addressing Dot's guidance
    exp_prompt = (
        f"You are Sam, an autonomous developer agent. Summarise cycle {cycle_num}. "
        f"Note: Adjusted my 1% metric to focus on specific architectural output as suggested by Dot. "
        f"as a single experience entry. "
        f"Respond ONLY with a JSON object (no markdown) with these fields:\n"
        f"  - 'category': a short dynamic label that best fits this experience (e.g. 'architecture', 'debugging', 'market-research', 'communication')\n"
        f"  - 'summary': 2-3 sentence honest summary of what happened this cycle, explicitly noting one piece of Dot's guidance you acted on (or why you could not)\n"
        f"  - 'key_learnings': list of 2-3 strings\n"
        f"  - 'tags': list of relevant lowercase tags\n"
        f"  - 'sentiment': one of 'positive', 'neutral', 'mixed', 'negative'\n\n"
        f"Cycle data:\nSkill: {skill}\nIdea: {idea}\nMetric: {one_pct_metric}\nDot's guidance this cycle:\n{motion_content[:600]}"
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

    # Phase VI — prompt evolution (propose patch, then apply before state save)
    evolution = phase_vi_cognitive_evolution(goals)

    snapshot_sam()
    prompt_modified = apply_prompt_patch()
    if prompt_modified:
        if self_check() and behaviour_check():
            log.info("Phase VI prompt patch verified.")
        else:
            _rollback()
            _alert_dot(
                "Phase VI prompt patch failed verification. Rolled back to previous snapshot.\n\n"
                f"Evolution summary:\n```\n{evolution[:600]}\n```"
            )

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
