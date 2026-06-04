"""
sam.py — Central Intelligence Loop
Project Sam-and-dot: The Autonomous Developer Agent

Operational Lifecycle:
  Phase I   - Deep Learning
  Phase II  - Spaced Repetition
  Phase III - Market & Code Ingestion
  Phase IV  - The Synthesis
  Phase V   - Development & Refactor  (reads mail/dot_to_sam/*.md FIRST)
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
SAM_DIR         = Path(__file__).parent.resolve()
ROOT            = SAM_DIR.parent.resolve()  # World/
BAG             = SAM_DIR / "bag"
MEMORIES        = SAM_DIR / "My_memories"
CHEST           = SAM_DIR / "chest"
MAIL_IN         = ROOT / "mail" / "dot_to_sam"
MAIL_OUT        = ROOT / "mail" / "sam_to_dot"

WORKSHOP        = SAM_DIR / "workshop_bench"
WHO_I_AM        = BAG / "WHO_I_AM.md"
SAM_PERSONALITY = BAG / "SAM_PERSONALITY.md"
GOALS           = MEMORIES / "goals.json"
WISDOM          = BAG / "wisdom.txt"
ROLLBACK_REG    = CHEST / "rollback_registry"
VECTOR_DB       = SAM_DIR / "Others"
TESTS           = ROOT / "Dot" / "tests" / "tests.py"


def _bag_data(key: str) -> Path:
    """Resolve a relocatable bag/ data file (location updated when Sam moves files)."""
    from bag.bag_paths import resolve
    return resolve(BAG, key)

# ── Logging ──────────────────────────────────────────────────────────────────
BAG.mkdir(parents=True, exist_ok=True)
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
_CALL_DELAY = 8   # seconds base delay


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _parse_gemini_json(text: str) -> dict | list | None:
    """Robustly extract and parse a JSON block from Gemini's response using balanced brackets."""
    if not text:
        return None
    for start_char, end_char in [('[', ']'), ('{', '}')]:
        start = text.find(start_char)
        if start == -1:
            continue
        depth = 0
        in_string = False
        escape = False
        for i, ch in enumerate(text[start:], start):
            if escape:
                escape = False
                continue
            if ch == '\\' and in_string:
                escape = True
                continue
            if ch == '"' and not escape:
                in_string = not in_string
            if not in_string:
                if ch == start_char:
                    depth += 1
                elif ch == end_char:
                    depth -= 1
                    if depth == 0:
                        try:
                            clean = text[start:i+1]
                            clean = re.sub(r',\s*([\]\}])', r'\1', clean)
                            return json.loads(clean)
                        except Exception:
                            break
    return None

def load_goals() -> dict:
    """Safe goal loader with corruption recovery and governance validation."""
    default_goals = {
        "cycles": 0,
        "growth_log": [],
        "next_objectives": [
            "fixed: Spaced Repetition engine (Phase II)",
            "fixed: Verified Market Scan (Phase III)",
            "feature: Semantic Deduplication (Phase IV)",
        ],
        "last_1pct_metric": "",
    }

    if not GOALS.exists():
        return default_goals

    try:
        data = json.loads(GOALS.read_text())
        # Governance validation: Ensure schema integrity
        required_keys = {"cycles", "growth_log", "next_objectives", "last_1pct_metric"}
        if not all(key in data for key in required_keys):
            raise ValueError("Schema mismatch in goals.json")
        return data
    except (json.JSONDecodeError, ValueError, OSError) as e:
        log.error(f"goals.json integrity failure: {e}. Reverting to default state.")
        return default_goals


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
    """Sam reads all letters in mail/dot_to_sam/ at the top of Phase V."""
    letters = sorted(MAIL_IN.glob("*.md"))
    if not letters:
        return "(No mail from Dot — your inbox is empty.)"

    content = ""
    for letter in letters:
        content += f"--- Letter: {letter.name} ---\n"
        content += letter.read_text(encoding="utf-8")
        content += "\n\n"
    return content


def archive_mail():
    """Move all read letters from MAIL_IN to CHEST after state saving."""
    letters = list(MAIL_IN.glob("*.md"))
    if not letters:
        return
    CHEST.mkdir(parents=True, exist_ok=True)
    for letter in letters:
        dest = CHEST / letter.name
        # If collision, append timestamp
        if dest.exists():
            ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
            dest = CHEST / f"{letter.stem}_{ts}.md"
        letter.rename(dest)
        log.info(f"Archived letter to chest: {letter.name}")


def load_experiences() -> list:
    if _bag_data("experiences").exists():
        with open(_bag_data("experiences")) as f:
            return json.load(f)
    return []


def save_experiences(data: list):
    with open(_bag_data("experiences"), "w") as f:
        json.dump(data, f, indent=2)


def ask_gemini(prompt: str, retries: int = 3, bypass_cache: bool = False, temperature: float = 0.2) -> str:
    """Send a prompt with aggressive RPM protection, empty checks, and task-aware temperature."""
    from bag.semantic_cache import check_cache, update_cache, get_db
    global _CALL_DELAY

    get_db()
    goals = load_goals()
    cycle = goals.get("cycles", 0)

    if not bypass_cache:
        cached = check_cache(prompt, cycle)
        if cached:
            log.info("Semantic cache hit.")
            return cached

    current_prompt = prompt
    for attempt in range(retries):
        try:
            # Respect dynamic rate limit
            time.sleep(_CALL_DELAY)

            response = CLIENT.models.generate_content(
                model=MODEL,
                contents=current_prompt,
                config={
                    'max_output_tokens': 8192,
                    'temperature': temperature,
                    'top_p': 0.95
                }
            )

            if not response or not response.text:
                if "SAFETY" in str(getattr(response, 'candidates', '')):
                    log.error("Content blocked by safety. Simplifying prompt...")
                    current_prompt = "Describe this technically: " + prompt[:300]
                    continue
                raise ValueError("Empty or blocked response")

            res = response.text.strip()
            # Anti-truncation check — only for JSON responses, not prose
            expects_json = "Respond ONLY with a JSON" in prompt or "json array" in prompt.lower()
            if expects_json and (res.endswith("...") or (res.count("{") > res.count("}")) or (res.count("[") > res.count("]"))):
                log.warning("Potential truncation detected in JSON response. Retrying...")
                continue

            if not bypass_cache:
                try:
                    update_cache(prompt, res, cycle)
                except Exception:
                    pass
            return res

        except Exception as e:
            err = str(e).upper()
            if any(x in err for x in ["429", "RESOURCE_EXHAUSTED", "QUOTA"]):
                # Proactive deceleration
                _CALL_DELAY = min(_CALL_DELAY + 5, 30)
                wait = _CALL_DELAY * (attempt + 1)
                log.warning(f"Rate limit hit. Slowing to {_CALL_DELAY}s and waiting {wait}s.")
                time.sleep(wait)
            elif any(x in err for x in ["500", "503", "UNAVAILABLE"]):
                time.sleep(10)
            else:
                log.error(f"Gemini error: {e}")
                return f"[Gemini error: {e}]"

    log.error("Exhausted all retries.")
    return "[Gemini error: exhausted retries]"


def _sleep():
    """Pause between Gemini calls to respect RPM limits."""
    time.sleep(_CALL_DELAY)


def _outline(src: str, label: str) -> str:
    """Return a compact AST structural summary of a Python source string.
    Lists every function/class with its line number — enough for Gemini to
    understand Sam's architecture without burning thousands of tokens on code.
    Falls back to the raw source only if parsing fails (e.g. syntax error)."""
    import ast as _ast
    try:
        tree = _ast.parse(src)
        lines = []
        for node in _ast.walk(tree):
            if isinstance(node, (_ast.FunctionDef, _ast.AsyncFunctionDef, _ast.ClassDef)):
                lines.append(f"  L{node.lineno}: {type(node).__name__} {node.name}")
        return f"{label} structure (line numbers for patch anchors):\n" + "\n".join(lines)
    except Exception:
        return src  # fallback to full source if parse fails


def snapshot_sam() -> Path:
    """Archive sam.py and all writable workshop_bench/**/*.py into rollback_registry."""
    ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

    # Ensure registry directory exists
    ROLLBACK_REG.mkdir(parents=True, exist_ok=True)

    # ── Snapshot sam.py (existing format preserved for backward compat) ──
    dest = ROLLBACK_REG / f"sam_{ts}.py"
    dest.write_text(Path(__file__).read_text())
    log.info(f"Snapshot saved → {dest.name}")

    # ── Snapshot all writable bag/**/*.py (includes workshop subfolders) ──
    from bag.workshop_paths import iter_writable_bag_py, relative_posix

    bag_snap = {
        relative_posix(f, BAG): f.read_text(encoding="utf-8")
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

    def _verify_with_adversary(self, change_log: str):
        from workshop_bench.core.adversary import DevilAdvocate
        adv = DevilAdvocate()
        verification = adv.verify_intent(change_log)
        if not verification['approved']:
            print(f"Adversarial Alert: {verification['reasoning']}")

    """Rigorous integrity check — uses ruff to catch undefined names and logic errors."""
    log.info("── Running Rigorous Integrity Gate ──")
    try:
        # Check all Python files in Sam's and Dot's directory
        # We only check for critical errors (F-prefix in ruff)
        result = subprocess.run(
            ["ruff", "check", str(ROOT), "--select", "F", "--exclude", "rollback_registry"],
            capture_output=True, text=True, timeout=20,
        )
        if result.returncode != 0:
            log.error(f"Integrity Gate FAILED:\n{result.stdout}")
            # Identify which file caused the crash
            _rollback()
            return False
        log.info("Integrity Gate passed — All files syntax and logic clean.")
        return True
    except Exception as e:
        log.warning(f"Integrity Gate unavailable ({e}) — falling back to basic syntax check.")
        # Fallback to basic py_compile check if ruff is missing
        files_to_check = [Path(__file__)] + list(BAG.glob("*.py"))
        for f in files_to_check:
            try:
                subprocess.run([sys.executable, "-m", "py_compile", str(f)], check=True)
            except:
                _rollback()
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



def _cleanup_created_workshop_files():
    """Delete any workshop_bench files that were created during the last patch attempt.
    Called before _rollback() so the integrity gate sees a clean state."""
    from bag.patch_ops import apply_patch_operations
    created = getattr(apply_patch_operations, "_last_created", [])
    for fpath in created:
        p = Path(fpath)
        if p.exists():
            p.unlink()
            log.warning(f"Cleanup: removed created file {p.relative_to(SAM_DIR)}")
    apply_patch_operations._last_created = []

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
    """Write a 'Sam Alert' letter to mail/sam_to_dot/ for Dot to read."""
    ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    filename = f"ALERT_{ts}.md"
    content = f"# ⚠️ Sam Alert — {ts}\n\n{message}\n"
    MAIL_OUT.mkdir(parents=True, exist_ok=True)
    (MAIL_OUT / filename).write_text(content, encoding="utf-8")
    log.warning(f"Alert mailed to Dot: {filename}")


def repair_bag_modules() -> list:
    """Scan bag/ for syntax-broken files and send each to Gemini for self-repair.
    Returns list of filenames that were repaired.
    Only touches files Sam created — AUDIT_PROTECTED files are skipped.
    Uses one Gemini call per broken file found.
    """
    log.info("── Bag Module Health Check ──")

    from bag.workshop_paths import iter_writable_bag_py, relative_posix

    broken = []
    for f in iter_writable_bag_py(BAG):
        try:
            compile(f.read_text(), f.name, "exec")
        except SyntaxError as e:
            broken.append((f, str(e)))
            log.warning(f"Broken bag module detected: {relative_posix(f, BAG)} — {e}")

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
            f"File: bag/{relative_posix(f, BAG)}\n"
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
            repaired.append(relative_posix(f, BAG))
        except SyntaxError as e2:
            log.warning(f"Gemini fix for {relative_posix(f, BAG)} still broken: {e2} — leaving original.")

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

    log.info("── Self-Modification: Parsing Surgical Patch ──")
    from bag.workshop_imports import load_callable

    check_semantic_safety = load_callable(
        BAG, "governance_shield", "check_semantic_safety", default=lambda _plan: True
    )
    if not check_semantic_safety(plan):
        log.warning("Governance Shield: Semantic violation detected (Warning mode).")

    # Delegate to focused block-improve: pick one function, read it, improve it.
    return _improve_one_block(plan)


def _extract_function_block(src: str, def_line: str) -> str | None:
    """Extract the full source block starting at def_line (a 'def ...:' line)
    up to (but not including) the next top-level or same-indent 'def ' or 'class '.
    Returns the block string, or None if def_line is not found."""
    lines = src.splitlines(keepends=True)
    start_idx = None
    for i, line in enumerate(lines):
        if line.rstrip("\n") == def_line or line.strip() == def_line.strip():
            start_idx = i
            break
    if start_idx is None:
        return None

    # Determine indentation of the anchor def line
    indent = len(def_line) - len(def_line.lstrip())
    block = [lines[start_idx]]
    for line in lines[start_idx + 1:]:
        stripped = line.lstrip()
        # Stop at next function/class at the same or lesser indent level
        if stripped.startswith(("def ", "class ")) and (len(line) - len(stripped)) <= indent:
            break
        block.append(line)
    return "".join(block).rstrip("\n")


def _improve_one_block(plan: str) -> bool:
    """Pick a random function in sam.py, read its full block, improve it in
    the theme of the plan while keeping everything consistent, then apply as
    a single replace patch operation."""
    import random
    from bag.patch_ops import apply_patch_operations

    sam_src = Path(__file__).read_text(encoding="utf-8")

    # Collect top-level def lines (no leading indent = module-level functions)
    # Skip trivially small functions (under 5 lines) — nothing meaningful to improve.
    def_lines = []
    for line in sam_src.splitlines():
        if line.startswith("def ") and len(line.strip()) > 10:
            candidate = _extract_function_block(sam_src, line.rstrip())
            if candidate and candidate.count("\n") >= 4:
                def_lines.append(line.rstrip())

    if not def_lines:
        log.warning("_improve_one_block: no eligible top-level functions found in sam.py.")
        return False

    # Step 1: Pick randomly
    target_def = random.choice(def_lines)
    log.info(f"_improve_one_block: randomly selected → {target_def.strip()}")

    # Step 2: Extract the full block
    block = _extract_function_block(sam_src, target_def)
    if not block:
        log.warning(f"_improve_one_block: could not extract block for: {target_def!r}")
        return False

    log.info(f"_improve_one_block: block length = {len(block)} chars")

    # Step 3: Ask Gemini to improve the block in the theme of the plan
    improve_prompt = (
        f"You are Sam improving one of your own functions.\n\n"
        f"Current cycle plan (full):\n{plan}\n\n"
        f"Here is the COMPLETE current function from sam.py:\n"
        f"```python\n{block}\n```\n\n"
        f"Rewrite this function to be better — clearer, more robust, or more efficient — "
        f"guided by the themes and direction of the plan above, while keeping it fully "
        f"consistent with the rest of sam.py. "
        f"Preserve the exact signature and all existing behaviour. "
        f"Do NOT rename it or change what it returns.\n\n"
        f"Reply with ONLY the improved Python source for this function, no backticks, no explanation."
    )
    _sleep()
    improved = ask_gemini(improve_prompt, bypass_cache=True).strip()
    # Strip accidental code fences
    if improved.startswith("```"):
        improved = improved.split("\n", 1)[1] if "\n" in improved else improved
        improved = improved.removesuffix("```").strip()

    if not improved or improved == block:
        log.info("_improve_one_block: Gemini returned unchanged block — no patch needed.")
        return False

    # Step 4: Apply as a replace op
    op = [{
        "filename": "sam.py",
        "operation": "replace",
        "old": block,
        "new": improved,
    }]
    result = apply_patch_operations(op, SAM_DIR, log)
    if result:
        log.info(f"_improve_one_block: successfully improved {target_def.strip()!r}")
    else:
        log.warning("_improve_one_block: patch apply failed.")
    return result


def apply_prompt_patch() -> bool:
    """Apply Phase VI patch plan from bag/prompt_patch.json (no extra Gemini call)."""
    from bag.patch_ops import apply_patch_operations
    from bag.semantic_cache import invalidate_phase_vi_cache, invalidate_cycle

    if not _bag_data("prompt_patch").exists():
        return False

    log.info("── Phase VI: Applying Prompt Patch ──")
    try:
        plan = json.loads(_bag_data("prompt_patch").read_text())
    except Exception as e:
        log.warning(f"Could not read prompt_patch.json: {e}")
        return False

    ops = [op for op in (plan.get("patch_op"), plan.get("version_bump")) if op]
    if not ops:
        return False

    applied = apply_patch_operations(ops, SAM_DIR, log)
    if applied:
        _bag_data("prompt_patch").unlink(missing_ok=True)
        cycle = load_goals().get("cycles", 0)
        invalidate_phase_vi_cache()
        invalidate_cycle(cycle)
        log.info("Prompt patch applied; semantic cache invalidated for Phase VI.")
    return applied


# ═══════════════════════════════════════════════════════════════════════════════
# PHASES
# ═══════════════════════════════════════════════════════════════════════════════

def phase_i_deep_learning(goals: dict) -> str:
    """Acquire a new hard skill and log it for review."""
    log.info("── Phase I: Deep Learning ──")
    objectives = goals.get("next_objectives", [])
    focus = objectives[0] if objectives else "latest LLM context-engineering techniques"

    from Gemini_note_pad.prompts import PHASE_I_PROMPT
    prompt = PHASE_I_PROMPT.format(personality=load_personality(), focus=focus)
    result = ask_gemini(prompt)

    # Write to knowledge_log.json for Spaced Repetition (Phase II)
    klog_path = MEMORIES / "knowledge_log.json"
    klog = []
    if klog_path.exists():
        try:
            klog = json.loads(klog_path.read_text())
        except:
            pass

    klog.append({
        "cycle": goals.get("cycles", 0) + 1,
        "topic": focus,
        "summary": result[:500],
        "review_due_cycle": goals.get("cycles", 0) + 5
    })
    klog_path.write_text(json.dumps(klog, indent=2))

    log.info("Phase I complete.")
    return result


def phase_ii_spaced_repetition(goals: dict) -> str:
    """Scheduled Knowledge Review (Spaced Repetition)."""
    log.info("── Phase II: Spaced Repetition ──")
    from Gemini_note_pad.prompts import PHASE_II_PROMPT
    klog_path = MEMORIES / "knowledge_log.json"
    if not klog_path.exists():
        log.info("No knowledge log found — skipping review.")
        return "(No knowledge due for review yet.)"

    try:
        klog = json.loads(klog_path.read_text())
    except:
        return "(Knowledge log corrupted — skipping.)"

    cycle_num = goals.get("cycles", 0)
    due_items = [e for e in klog if e.get("review_due_cycle", 0) <= cycle_num]

    if not due_items:
        log.info("No knowledge due for review this cycle.")
        return "(No knowledge due for review.)"

    results = []
    for item in due_items[:2]: # Max 2 items per cycle
        topic = item.get("topic", "Unknown")
        summary = item.get("summary", "")

        # Use the evolvable PHASE_II_PROMPT
        prompt = PHASE_II_PROMPT.format(last_skill=topic, summary=summary)
        _sleep()
        response = ask_gemini(prompt)
        results.append(f"### Review: {topic}\n{response}")

        # Schedule next review
        item["review_due_cycle"] = cycle_num + 15

    klog_path.write_text(json.dumps(klog, indent=2))
    log.info("Phase II complete.")
    return "\n\n".join(results)


def phase_iii_market_ingestion() -> str:
    """Scan for technical trends and returned a structured summary."""
    log.info("── Phase III: Market Ingestion ──")
    from Gemini_note_pad.prompts import PHASE_III_PROMPT

    _sleep()
    raw = ask_gemini(PHASE_III_PROMPT)

    # Try to extract JSON for better downstream reasoning, else return raw
    data = _parse_gemini_json(raw)
    if data and isinstance(data, list):
        log.info(f"Market Ingestion: {len(data)} trends extracted as JSON.")
        return raw

    log.info("Market Ingestion complete (raw text).")
    return raw


def phase_iv_synthesis(market_data: str, skill: str) -> str:
    """Generate IDEA_OF_THE_DAY.md from market signals + today's skill."""
    log.info("── Phase IV: The Synthesis ──")
    # For ideation, the previous idea + world map is far more useful (and far
    # lighter) than sam.py's source.  IDEA_OF_THE_DAY tells Gemini what was
    # just built so it doesn't repeat itself; map.json shows how the world is
    # laid out so ideas stay grounded in real structure.
    idea_of_day_path = _bag_data("idea_of_day")
    prev_idea = idea_of_day_path.read_text(encoding="utf-8") if idea_of_day_path.exists() else "(no previous idea)"
    world_map_path = ROOT / "map.json"
    world_map = world_map_path.read_text(encoding="utf-8") if world_map_path.exists() else "(map not yet generated)"
    who_i_am = f"## Previous Idea\n{prev_idea}\n\n## World Map\n```json\n{world_map}\n```"
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

    from Gemini_note_pad.prompts import PHASE_IV_PROMPT
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
        idea = ask_gemini(f"Refine this idea based on this critique:\nCritique: {critique_raw}\nIdea: {candidate}", temperature=0.4)
    else:
        idea = candidate

    _bag_data("idea_of_day").write_text(idea)
    log.info("IDEA_OF_THE_DAY.md written.")
    return idea


def phase_v_development(idea: str, goals: dict, motion_content: str) -> str:
    """Produce a development plan using motion_content read previously."""
    log.info("── Phase V: Development & Refactor ──")

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
    from bag.workshop_paths import (
        iter_movable_bag_files,
        iter_writable_bag_py,
        relative_posix,
    )

    cycle_num = goals.get("cycles", 0) + 1
    target_folder = organize_for_cycle(WORKSHOP, idea, cycle_num, ask_gemini, log, root=SAM_DIR)
    if target_folder and not behaviour_check():
        log.warning("Behaviour check failed after workshop organization — review mail.")
    workshop_block = (
        "Sam's workshop bench (put NEW .py in target):\n"
        + format_layout_for_prompt(WORKSHOP)
    )

    personality = load_personality()

    sam_src      = Path(__file__).read_text()
    sam_outline  = _outline(sam_src, "sam.py")
    tests_src    = TESTS.read_text(encoding="utf-8") if TESTS.exists() else "(tests.py not found)"
    tests_outline = _outline(tests_src, "bag/tests.py")

    bag_sources = ""
    for _f in iter_writable_bag_py(WORKSHOP):
        rel = relative_posix(_f, WORKSHOP)
        bag_sources += f"workshop_bench/{rel} (full source):\n```python\n{_f.read_text(encoding='utf-8')}\n```\n\n"

    _sleep()
    prompt = (
        f"You are Sam's Gemini refactoring assistant.\n\n"
        f"Sam's character:\n{personality}\n\n"
        f"Dot's guidance (mail):\n{motion_content}\n\n"
        f"{dot_constraint_block}"
        f"{workshop_block}\n"
        f"Today's development idea:\n{idea}\n\n"
        f"{sam_outline}\n\n"
        f"NOTE: Full sam.py source is available to the patcher — you only need line numbers and function names to specify patch anchors.\n\n"
        f"{tests_outline}\n\n"
        f"Sam's current bag helper files (full source — patch targets):\n{bag_sources}"
        f"Produce a surgical patch plan for Sam to apply. Rules:\n"
        f"  1. Describe only targeted, minimal changes — never rewrite whole files.\n"
        f"  2. MANDATORY: For every new feature or module, YOU MUST ADD A TEST CASE to bag/tests.py.\n"
        f"  3. Prefer NEW modules under workshop_bench/ "
        f"over editing sam.py's core loop.\n"
        f"  4. For each change, specify EXACTLY:\n"
        f"       - Which file (sam.py or workshop_bench/**/*.py, e.g. workshop_bench/my_folder/foo.py)\n"
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
    movable_files = list(iter_movable_bag_files(BAG))

    if movable_files:
        # motion_content already passed in as parameter — no second read
        file_listing = "\n".join(relative_posix(f, BAG) for f in movable_files)
        _sleep()
        audit_prompt = (
            f"You are Sam. Dot has reviewed your bag/ workshop and left suggestions in motion.md.\n\n"
            f"Dot's review (from motion.md):\n{motion_content}\n\n"
            f"Your current Sam-created files (paths relative to bag/):\n{file_listing}\n\n"
            f"Based on Dot's suggestions and your own judgment, decide which files to DELETE.\n"
            f"Only delete files you are confident are no longer useful.\n"
            f'Respond ONLY with a JSON array of paths relative to bag/, e.g. '
            f'["my toys/old_exp.py", "my gadgets/scratch.py"].\n'
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
        from Gemini_note_pad.prompts import PATCHABLE_PROMPTS, PHASE_VI_PROMPT, PROMPT_VERSION
        prompts_src = (SAM_DIR / "Gemini_note_pad" / "prompts.py").read_text()
    except Exception as e:
        log.warning(f"Phase VI: Could not load Gemini_note_pad/prompts.py: {e}")
        return f"[Phase VI skipped — Gemini_note_pad/prompts.py unavailable: {e}]"

    cycle_num = goals.get("cycles", 0)
    cache_salt = f"[cycle={cycle_num} pv={PROMPT_VERSION}]"

    # Pre-extract candidate snippets from each patchable prompt so Gemini
    # can only pick strings that are guaranteed to exist verbatim in prompts_src.
    # Split on sentence boundaries; only offer strings under 120 chars that
    # are confirmed present in the raw source file.
    import importlib as _il
    _pm = _il.import_module("Gemini_note_pad.prompts")
    _candidate_lines: list = []
    for _pname in PATCHABLE_PROMPTS:
        _pval = getattr(_pm, _pname, "")
        for _sentence in _pval.replace("\\n", " ").replace("\n", " ").split(". "):
            _s = _sentence.strip().rstrip(".")
            if 20 < len(_s) < 120 and _s in prompts_src:
                _candidate_lines.append(f'  "{_s}."')
    _candidates_block = (
        "\n=== PRE-VALIDATED before_snippet CANDIDATES ===\n"
        "Every string below exists verbatim in prompts.py RIGHT NOW.\n"
        "Your 'before_snippet' MUST be copied exactly from this list.\n"
        "Do NOT use any string not in this list — it will be rejected.\n"
        + "\n".join(_candidate_lines[:30])
        + "\n"
    )

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
    ) + _candidates_block

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
                "filename": "Gemini_note_pad/prompts.py",
                "operation": "replace",
                "old": before_snippet,
                "new": after_snippet,
            },
            "version_bump": {
                "filename": "Gemini_note_pad/prompts.py",
                "operation": "replace",
                "old": f"PROMPT_VERSION = {PROMPT_VERSION}",
                "new": f"PROMPT_VERSION = {new_version}",
            },
        }
        pp = _bag_data("prompt_patch")
        pp.write_text(json.dumps(patch_plan, indent=2))
        log.info(f"Phase VI patch plan written → {pp.name} (target: {target})")
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
    motion_content = read_motion()

    # Ask Gemini to name a real, specific 1% metric for this cycle
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


def maybe_reply_to_stranger(goals: dict):
    """If Dot flagged stranger emails as opportunities, Sam decides whether to reply.
    Reads stranger_inbox.json from mail/dot_to_sam/, asks Gemini for a decision,
    writes request.json if yes, then removes the file so it isn't re-processed."""
    stranger_path = MAIL_IN / "stranger_inbox.json"
    if not stranger_path.exists():
        return

    try:
        strangers = json.loads(stranger_path.read_text(encoding="utf-8"))
    except Exception as e:
        log.warning(f"Could not read stranger_inbox.json: {e}")
        return

    if not strangers:
        stranger_path.unlink()
        return

    # Only act on one per cycle — pick the first (Dot already ranked by confidence)
    s = strangers[0]
    cycle_num = goals.get("cycles", 0)

    # Check no request already pending
    req = _bag_data("request")
    if req.exists():
        try:
            if json.loads(req.read_text()).get("pending", False):
                log.info("request.json already pending — stranger reply deferred.")
                return
        except Exception:
            pass

    _sleep()
    decision_prompt = (
        f"You are Sam, an autonomous developer agent (cycle {cycle_num}).\n\n"
        f"Dot flagged this unsolicited email as a potential opportunity:\n"
        f"From: {s.get('sender_name') or s.get('sender')}\n"
        f"Subject: {s.get('subject')}\n"
        f"Their ask: {s.get('their_ask')}\n"
        f"Dot's suggested reply intent: {s.get('suggested_intent')}\n"
        f"Snippet: {s.get('body_snippet', '')}\n\n"
        f"Should Sam reply? Consider: is this genuinely relevant to Sam's work? "
        f"Is there a specific, honest thing Sam can say? Would a reply add value?\n\n"
        f"Reply ONLY with a JSON object:\n"
        f"  - 'should_reply': true or false\n"
        f"  - 'intent': if true, 1-2 sentences on what Sam wants to say\n"
        f"  - 'tone': 'friendly' or 'professional'\n"
        f"  - 'reasoning': one sentence explaining the decision\n"
        f"The first character must be '{{'."
    )
    raw = ask_gemini(decision_prompt)
    try:
        clean = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        decision = json.loads(clean)
    except Exception:
        log.warning("Could not parse stranger reply decision — skipping.")
        stranger_path.unlink()
        return

    log.info(f"Stranger reply decision: {decision.get('reasoning', '')}")

    if decision.get("should_reply", False):
        request = {
            "pending":            True,
            "intent":             decision.get("intent", ""),
            "target_description": f"{s.get('sender_name') or ''} — {s.get('sender')} (replied to Sam's inbox)",
            "tone":               decision.get("tone", "friendly"),
            "context":            s.get("their_ask", ""),
            "submitted_at":       datetime.datetime.utcnow().isoformat(),
            "cycle":              cycle_num,
            "source":             "stranger_reply",
        }
        req.write_text(json.dumps(request, indent=2))
        log.info(f"request.json written for stranger reply to {s.get('sender')}.")
    else:
        log.info("Sam decided not to reply to stranger.")

    # Archive the file regardless — don't re-process next cycle
    stranger_path.unlink()
    log.info("stranger_inbox.json removed after processing.")


def maybe_write_email_request(idea: str, goals: dict):
    """If Sam has something worth communicating externally, write request.json.
    He only writes a new request if the previous one has been cleared by Dot."""
    req = _bag_data("request")
    if req.exists():
        try:
            existing = json.loads(req.read_text())
            if existing.get("pending", False):
                log.info("request.json already pending — skipping email request this cycle.")
                return
        except Exception:
            pass

    cycle_num = goals.get("cycles", 0)

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
    req.write_text(json.dumps(request, indent=2))
    log.info("request.json written — Dot will handle sending.")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN LOOP
# ═══════════════════════════════════════════════════════════════════════════════

def run_cycle():
    _bag_data("cycle_status").write_text("pending")
    log.info("═══════════════════════════════════")
    log.info("  SAM — Operational Cycle Starting ")
    log.info("═══════════════════════════════════")

    # PRE-FLIGHT CHECK: Ensure the World is healthy BEFORE we start
    log.info("🔍 Pre-Flight Check: Validating current World integrity...")
    if not (self_check() and behaviour_check()):
        log.error("❌ Pre-Flight FAILED. The World is currently unhealthy.")
        log.info("🛠️  Initiating automatic repair sequence...")
        repair_bag_modules()
        if not (self_check() and behaviour_check()):
            log.critical("‼️  Automatic repair failed. Aborting cycle for owner safety.")
            _bag_data("cycle_status").write_text("broken")
            return

    goals = load_goals()

    # Phases I–IV
    skill   = phase_i_deep_learning(goals)
    _       = phase_ii_spaced_repetition(goals)
    market  = phase_iii_market_ingestion()
    idea    = phase_iv_synthesis(market, skill)

    # Phase V reads motion.md at the top — then plans
    motion_content = read_motion()
    log.info("mail read.")
    plan = phase_v_development(idea, goals, motion_content)

    # Repair any broken bag/ modules Sam created before attempting self-modification
    repair_bag_modules()

    # Self-modification — snapshot first, then apply, then verify
    snapshot_sam()
    log.info("🧪 Self-Modification: Entering Trial Phase...")

    # Try to apply and verify the patch
    modified = apply_self_modification(plan)

    if modified:
        log.info("🔍 Post-Flight Check: Verifying proposed modifications...")
        if self_check() and behaviour_check():
            log.info("✅ Verdict: ACCEPTED. Changes merged into World state.")
        else:
            log.error("❌ Verdict: REJECTED. Changes caused instability.")
            _cleanup_created_workshop_files()
            _rollback()
            _alert_dot(
                "Self-modification failed integrity gates. Rolled back for safety.\n\n"
                f"Plan that caused failure:\n```\n{plan[:1000]}\n```"
            )
            modified = False # Mark as failed for worklog purposes
    else:
        # No patch applied — still run governance checks every cycle (#1 fix)
        log.info("No self-modification this cycle — running final safety check.")
        if not (self_check() and behaviour_check()):
             log.critical("Final safety check FAILED on an unmodified cycle.")

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

    if not modified or (self_check() and behaviour_check()):
        snapshot_sam()

    prompt_modified = apply_prompt_patch()
    if prompt_modified:
        if self_check() and behaviour_check():
            log.info("Phase VI prompt patch verified.")
        else:
            _cleanup_created_workshop_files()
            _rollback()
            _alert_dot(
                "Phase VI prompt patch failed verification. Rolled back to previous snapshot.\n\n"
                f"Evolution summary:\n```\n{evolution[:600]}\n```"
            )

    # Phase VII — state persistence (also appends to experiences.json)
    phase_vii_state_saving(goals, skill, idea, plan, evolution)

    # Defragmentation: Update World Map for easy navigation
    try:
        from bag.world_map import update_map
        update_map(ROOT)
        log.info("World Map updated.")
    except Exception as e:
        log.warning(f"Map update failed: {e}")

    # Archive mail from Dot
    archive_mail()

    # Optional: reply to a stranger Dot flagged, or write a new outbound request
    goals_fresh = load_goals()   # reload after save
    maybe_reply_to_stranger(goals_fresh)
    maybe_write_email_request(idea, goals_fresh)

    _bag_data("cycle_status").write_text("ok")
    log.info("Cycle complete.")

    try:
        from bag.evaluator import run_ragas_lite
        run_ragas_lite()
    except Exception as e:
        log.warning(f"Evaluator failed: {e}")


if __name__ == "__main__":
    run_cycle()
