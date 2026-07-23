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
import itertools
import sys
import json

# from workshop_bench.infrastructure.state.observer import ScratchpadEntry, Status, log_entry
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

def _parse_gemini_json(text: str, schema=None) -> dict | list | None:
    """Robustly extract and parse JSON, validating against an optional Pydantic schema."""
    if not text: return None
    # Extract content between first '[' or '{' and last ']' or '}'
    start = re.search(r'[\[\{]', text)
    end = re.search(r'[\]\}](?!.*[\]\}])', text)
    if not start or not end: return None
    try:
        data = json.loads(text[start.start():end.end()])
        return schema.parse_obj(data) if schema else data
    except json.JSONDecodeError as e:
        log.error(f"JSON decode failed at line {e.lineno}, col {e.colno}: {e.msg}")
        return None

def load_goals() -> dict:
    """Safe goal loader with corruption recovery."""
    if GOALS.exists():
        try:
            return json.loads(GOALS.read_text())
        except (json.JSONDecodeError, OSError) as e:
            log.error(f"goals.json corrupted: {e}. Restoring from backup or defaults.")
            # Restore logic could go here; for now, return default
    return {
        "cycles": 0,
        "growth_log": [],
        "next_objectives": [
            "fixed: Spaced Repetition engine (Phase II)",
            "fixed: Verified Market Scan (Phase III)",
            "feature: Semantic Deduplication (Phase IV)",
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


def _is_truncated(text: str, expects_json: bool) -> bool:
    """Detect whether a Gemini response was cut off mid-generation."""
    if text.endswith("..."):
        return True
    if expects_json:
        if text.count("{") > text.count("}"):
            return True
        if text.count("[") > text.count("]"):
            return True
    # Detect code truncated mid-definition (e.g. "def foo(x, max_r" with no closing paren)
    last_line = text.rstrip().splitlines()[-1] if text.strip() else ""
    if re.search(r"def \w+\([^)]*$", last_line):
        return True
    # Unclosed code block
    if text.count("```") % 2 != 0:
        return True
    return False


def _stitch_gemini(initial: str, temperature: float, max_continuations: int = 3) -> str:
    """If initial response looks truncated, ask Gemini to continue and stitch chunks together."""
    global _CALL_DELAY
    result = initial
    for i in range(max_continuations):
        expects_json = result.lstrip().startswith(("[", "{"))
        if not _is_truncated(result, expects_json):
            break
        log.warning(f"Truncation detected — requesting continuation {i + 1}/{max_continuations}.")
        time.sleep(_CALL_DELAY)
        try:
            cont_response = CLIENT.models.generate_content(
                model=MODEL,
                contents=f"Your previous response was cut off. Continue exactly from where you stopped, with no preamble or repeated text:\n\n{result[-300:]}",
                config={
                    'max_output_tokens': 8192,
                    'temperature': temperature,
                    'top_p': 0.95
                }
            )
            if cont_response and cont_response.text:
                chunk = cont_response.text.strip()
                # Avoid re-appending text already present at the seam
                overlap = len(chunk) // 4
                if result.endswith(chunk[:overlap]):
                    result = result + chunk[overlap:]
                else:
                    result = result + "\n" + chunk
                log.info(f"Continuation {i + 1} stitched ({len(chunk)} chars).")
            else:
                log.warning("Continuation response was empty — stopping stitch.")
                break
        except Exception as e:
            log.warning(f"Continuation call failed: {e} — stopping stitch.")
            break
    return result


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

    expects_json = "Respond ONLY with a JSON" in prompt or "json array" in prompt.lower()
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

            # Stitch continuations if truncated (covers JSON and prose/code)
            res = _stitch_gemini(res, temperature)

            # Final truncation check — retry the whole call if still incomplete
            if expects_json and _is_truncated(res, expects_json):
                log.warning("Response still truncated after stitching. Retrying full call...")
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
    """Return a structural summary of a Python source string for patch anchoring.
    Small functions (<=50 lines) get their full body so anchors can be copied
    character-for-character. Large functions get a 10-line preview with a note.
    Falls back to the raw source if parsing fails."""
    import ast as _ast
    THRESHOLD = 50
    src_lines = src.splitlines()
    try:
        tree = _ast.parse(src)
        entries = []
        for node in _ast.iter_child_nodes(tree):
            if not isinstance(node, (_ast.FunctionDef, _ast.AsyncFunctionDef, _ast.ClassDef)):
                continue
            start = node.lineno - 1
            end = node.end_lineno
            length = end - start
            if length <= THRESHOLD:
                body = "\n".join(src_lines[start:end])
            else:
                preview = "\n".join(src_lines[start:start + 10])
                body = (
                    f"{preview}\n"
                    f"    # ... {length} lines total (L{node.lineno}–{node.end_lineno})"
                    f" — use exact anchor strings from these lines"
                )
            entries.append(body)
        return f"{label} (full bodies for anchoring):\n\n" + "\n\n".join(entries)
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

    # ── Snapshot all writable workshop_bench/**/*.py ──
    from bag.workshop_paths import iter_writable_bag_py, relative_posix

    bag_snap = {
        relative_posix(f, WORKSHOP): f.read_text(encoding="utf-8")
        for f in iter_writable_bag_py(WORKSHOP)
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

    # ── Restore workshop_bench/*.py files from the corresponding bag snapshot ──
    ts = latest.stem[4:]   # strip "sam_" prefix
    bag_snap_path = ROLLBACK_REG / f"bag_{ts}.json"
    if bag_snap_path.exists():
        try:
            bag_snap = json.loads(bag_snap_path.read_text())
            for rel, content in bag_snap.items():
                target = WORKSHOP / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")
                log.warning(f"Rolled back workshop_bench/{rel}")
            log.warning(f"Workshop files restored from {bag_snap_path.name} ({len(bag_snap)} files)")
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
    """Scan workshop_bench/ for syntax-broken files and send each to Gemini for self-repair.
    Returns list of filenames that were repaired.
    Only touches files Sam created — AUDIT_PROTECTED files are skipped.
    Uses one Gemini call per broken file found.
    """
    log.info("── Bag Module Health Check ──")

    from bag.workshop_paths import iter_writable_bag_py, relative_posix

    broken = []
    for f in iter_writable_bag_py(WORKSHOP):
        try:
            compile(f.read_text(), f.name, "exec")
        except SyntaxError as e:
            broken.append((f, str(e)))
            log.warning(f"Broken workshop module detected: {relative_posix(f, WORKSHOP)} — {e}")

    if not broken:
        log.info("All bag modules are syntax-clean.")
        return []

    repaired = []
    for (f, error) in broken:
        original = f.read_text()
        log.info(f"Sending {f.name} to Gemini for self-repair...")
        _sleep()
        rel = relative_posix(f, WORKSHOP)
        prompt = (
            f"You are Sam, an autonomous developer. One of your workshop files has a syntax error.\n\n"
            f"File: workshop_bench/{rel}\n"
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
            repaired.append(rel)
        except SyntaxError as e2:
            log.warning(f"Gemini fix for {rel} still broken: {e2} — leaving original.")

    return repaired


def _dry_run_lint() -> tuple[bool, str]:
    """Run ruff over the World after a patch is applied but before the integrity gate.
    Returns (passed, error_output). Does NOT rollback — caller decides what to do."""
    try:
        result = subprocess.run(
            ["ruff", "check", str(ROOT), "--select", "F", "--exclude", "rollback_registry"],
            capture_output=True, text=True, timeout=20,
        )
        if result.returncode == 0:
            return True, ""
        return False, result.stdout.strip()
    except Exception as e:
        log.error(f"Dry-run lint failed/unavailable: {e}")
        return False, "Ruff missing or failed"


def _lint_fix_with_gemini(lint_errors: str) -> bool:
    """Feed ruff errors back to Gemini and apply a corrective patch. One attempt only.
    Returns True if a corrective patch was applied (whether or not it fully fixes lint)."""
    from bag.patch_ops import apply_patch_operations

    log.info("🔧 Lint errors detected — asking Gemini for a corrective patch...")

    # Collect current source of every file mentioned in the errors for context
    file_contexts = ""
    mentioned = set(re.findall(r"((?:sam\.py|workshop_bench/[^\s:]+\.py))", lint_errors))
    for rel in mentioned:
        target = SAM_DIR / rel
        if target.exists():
            file_contexts += f"\n### {rel} (current content):\n```python\n{target.read_text(encoding='utf-8')}\n```\n"

    prompt = (
        f"You are Sam's lint fixer. Ruff found the following errors after a patch was applied:\n\n"
        f"```\n{lint_errors}\n```\n"
        f"{file_contexts}\n"
        f"Produce a JSON array of surgical patch operations to fix ONLY these lint errors.\n"
        f"Respond ONLY with a JSON array — no markdown, no explanation, no preamble.\n\n"
        f"Rules:\n"
        f"  - 'filename': relative path from Sam's root (sam.py or workshop_bench/**/*.py)\n"
        f"  - 'operation': exactly one of: 'replace', 'delete'\n"
        f"  - For 'replace': 'old' (exact existing string) and 'new' (corrected string)\n"
        f"  - For 'delete': 'old' (exact string to remove)\n"
        f"  - 'old' must be an exact substring of the current file shown above.\n"
        f"  - Fix unused imports (F401) by removing them from the import line.\n"
        f"  - Fix undefined names (F821) by adding the missing import.\n"
        f"  - Keep changes minimal — touch only the lines ruff flagged.\n"
        f"  - Never supply a 'content' key.\n"
        f"  - If nothing can be fixed, return an empty array [].\n"
    )

    _sleep()
    raw = ask_gemini(prompt, bypass_cache=True)
    ops = _parse_gemini_json(raw)
    if not ops:
        log.warning("Lint-fix Gemini call returned no operations.")
        return False

    # Transitioning to state-machine execution
    applied = apply_patch_operations(ops, SAM_DIR, log)
    if applied:
        log.info("Corrective lint patch applied.")
    else:
        log.warning("Corrective lint patch had no applicable operations.")
    return applied


def _behaviour_fix_with_gemini(test_output: str, original_plan: str) -> bool:
    """Feed a failed behaviour-check output back to Gemini for a corrective patch.
    One attempt only. Returns True if a patch was applied (not necessarily passing)."""
    from bag.patch_ops import apply_patch_operations

    log.info("🔧 Behaviour check failed — asking Gemini for a corrective patch...")

    # Gather source of files the original plan touched
    file_contexts = ""
    mentioned = set(re.findall(r"((?:sam\.py|workshop_bench/[^\s:]+\.py))", original_plan))
    for rel in mentioned:
        target = SAM_DIR / rel
        if target.exists():
            file_contexts += f"\n### {rel} (current content):\n```python\n{target.read_text(encoding='utf-8')}\n```\n"

    tests_src = TESTS.read_text(encoding="utf-8") if TESTS.exists() else "(tests.py not found)"

    prompt = (
        f"You are Sam's self-correction assistant. A patch was applied but the behaviour "
        f"check (bag/tests.py) failed immediately after.\n\n"
        f"Failing test output:\n```\n{test_output[:1200]}\n```\n\n"
        f"The original patch plan that caused this:\n```\n{original_plan[:800]}\n```\n\n"
        f"bag/tests.py (so you know exactly what each test checks):\n```python\n{tests_src}\n```\n"
        f"{file_contexts}\n"
        f"Produce a JSON array of minimal surgical patch operations that fix the test failure.\n"
        f"Respond ONLY with a JSON array — no markdown, no explanation, no preamble.\n\n"
        f"Rules:\n"
        f"  - 'filename': relative path from Sam's root (sam.py or workshop_bench/**/*.py)\n"
        f"  - 'operation': exactly one of: 'replace', 'insert_after', 'delete'\n"
        f"  - 'old' / 'anchor' must be exact substrings of the current file shown above.\n"
        f"  - Fix only what the test failure demands — do not refactor anything else.\n"
        f"  - Ensure all imports needed by new code are present.\n"
        f"  - If nothing can be fixed safely, return an empty array [].\n"
    )

    _sleep()
    raw = ask_gemini(prompt, bypass_cache=True)
    ops = _parse_gemini_json(raw)
    if not ops:
        log.warning("Behaviour-fix Gemini call returned no operations.")
        return False

    applied = apply_patch_operations(ops, SAM_DIR, log)
    if applied:
        log.info("Corrective behaviour patch applied — re-verifying...")
    else:
        log.warning("Corrective behaviour patch had no applicable operations.")
    return applied


def apply_self_modification(plan: str) -> bool:
    """Ask Gemini to extract surgical patch operations from the plan and apply them.
    Uses bag/patch_ops.py for atomic file transactions.
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
    from bag.workshop_imports import load_callable

    check_semantic_safety = load_callable(
        BAG, "governance_shield", "check_semantic_safety", default=lambda _plan: True
    )
    if not check_semantic_safety(plan):
        log.warning("Governance Shield: Semantic violation detected (Warning mode).")

    # Inject actual source of files the plan mentions so 'old'/'anchor' strings can be copied exactly
    # Always include sam.py — it's almost always relevant and Gemini needs exact anchors from it
    mentioned = set(re.findall(r"(sam\.py|workshop_bench/[\w/]+\.py)", plan))
    mentioned.add("sam.py")
    file_contexts = ""
    for rel in sorted(mentioned):
        target = SAM_DIR / rel
        if target.exists():
            file_contexts += (
                f"\n### {rel} (current source — copy 'old'/'anchor' from here exactly):\n"
                f"```python\n{_outline(target.read_text(), rel)}\n```\n"
            )

    prompt = (
        f"You are Sam's surgical code patcher. Below is a development plan:\n\n{plan}\n\n"
        f"{file_contexts}"
        f"Extract any concrete file modifications as a JSON array of patch operations.\n"
        f"Each operation may include an optional 'rationale' field (1 sentence) explaining the change.\n"
        f"Respond ONLY with a JSON array — no markdown, no explanation, no preamble.\n\n"
        f"Each element must have:\n"
        f"  - 'filename'  : relative path from Sam's root. 'sam.py' or 'workshop_bench/**/*.py'. "
        f"Use 'workshop_bench/<folder>/<file>.py' for new standalone modules. sam.py may be modified to wire in existing workshop modules.\n"
        f"  - 'operation' : exactly one of: 'replace', 'insert_after', 'delete'\n"
        f"  - For 'replace': 'old' (exact existing string) and 'new' (replacement string)\n"
        f"  - For 'insert_after': 'anchor' (exact existing line), 'line_number' (integer), and 'new' (string to insert after it)\n"
        f"  - For 'delete': 'old' (exact existing string to remove)\n\n"
        f"CRITICAL RULES:\n"
        f"  - Never supply a 'content' key — full file rewrites are forbidden.\n"
        f"  - ALLOWED FILES ONLY: 'sam.py' and 'workshop_bench/**/*.py'. Any patch targeting\n"
        f"    bag/tests.py, bag/patch_ops.py, bag/governance_shield.py, or ANY other bag/ file\n"
        f"    will be silently rejected — do NOT waste operations on them.\n"
        f"  - MODULE PATHS: The prompts file is at 'Gemini_note_pad/prompts.py'.\n"
        f"    Import it as: from Gemini_note_pad.prompts import ...\n"
        f"    NEVER use 'bag.prompts' — that module does not exist and will crash Sam.\n"
        f"  - 'old' and 'anchor' must be exact substrings of the current file — copy them precisely.\n"
        f"  - Keep each operation as small as possible — one function, one block, one line.\n"
        f"  - sam.py changes are allowed — especially to import and call modules already built in workshop_bench/. Prefer workshop_bench/ only for new standalone logic.\n"
        f"  - If no concrete changes are needed, return an empty array [].\n\n"
        f"PYTHON CODE QUALITY RULES — every 'new' string must obey these:\n"
        f"  - Must be syntactically valid Python. Mentally parse it before including it.\n"
        f"  - Indentation must be correct: class methods indented 4 spaces inside their class,\n"
        f"    nested blocks indented a further 4 spaces each level. Never mix tabs and spaces.\n"
        f"  - A class body must never be left empty. If a class has no body yet, add 'pass'.\n"
        f"  - Never place a method definition outside its class block.\n"
        f"  - After a 'replace', the resulting file must remain structurally intact —\n"
        f"    check that the 'old' context around the change is not load-bearing for other blocks."
        f"  - IMPORTS — MANDATORY: Every name used in a 'new' string must be imported.\\n"
        f"    New files created via insert_after must declare ALL imports on the very first lines.\\n"
        f"    There are NO implicit imports in Python — logging, queue, threading, re, json, etc.\\n"
        f"    must each be imported explicitly. Missing imports cause ruff F821 and a full rollback.\\n"
        f"\\n"
        f"    CORRECT new file 'new' string example (imports first, always):\\n"
        f"      import logging\\n"
        f"      import queue\\n"
        f"      import threading\\n"
        f"      log = logging.getLogger('sam')\\n"
        f"      class BatchManager:\\n"
        f"          def __init__(self):\\n"
        f"              self.queue = queue.Queue()\\n"
        f"              self.lock = threading.Lock()\\n"
        f"\\n"
        f"    WRONG — will be REJECTED by ruff F821:\\n"
        f"      class BatchManager:\\n"
        f"          def __init__(self):\\n"
        f"              self.queue = queue.Queue()  # queue not imported — FAIL"
    )

    _sleep()
    raw = ask_gemini(prompt)

    operations = _parse_gemini_json(raw)
    if not operations:
        log.warning("No patch operations extracted.")
        log.info(f"Gemini patch response (first 200 chars): {raw[:200]}")
        return False

    applied = apply_patch_operations(operations, SAM_DIR, log)
    if not applied:
        return False

    # ── Dry-run lint gate: catch ruff errors before the integrity gate fires ──
    lint_ok, lint_errors = _dry_run_lint()
    if not lint_ok:
        log.warning(f"Dry-run lint found issues:\n{lint_errors}")
        _lint_fix_with_gemini(lint_errors)
        # Re-check once after the corrective patch — integrity gate is still the final arbiter
        lint_ok2, lint_errors2 = _dry_run_lint()
        if lint_ok2:
            log.info("✅ Dry-run lint clean after corrective patch.")
        else:
            log.warning(f"Dry-run lint still has issues after fix attempt:\n{lint_errors2}")
    else:
        log.info("✅ Dry-run lint clean.")

    return True


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
        with open(klog_path, 'r') as f:
            klog = json.load(f)
    except json.JSONDecodeError as e:
        log.error(f"Knowledge log corrupted: {e}")
        return "(Knowledge log corrupted — skipping.)"

    cycle_num = goals.get("cycles", 0)
    # Use iterator to filter due items without loading full list into memory
    due_items = list(itertools.islice((e for e in klog if e.get("review_due_cycle", 0) <= cycle_num), 2))

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
    # Use sam.py's AST outline as the architecture overview — it's the ground
    # truth of Sam's current structure, and _outline() keeps it to ~1 k tokens
    # instead of the 1 MB+ that WHO_I_AM.md balloons to (it embeds full source).
    who_i_am = _outline(Path(__file__).read_text(), "sam.py")
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
        f"Sam's current workshop files (full source — valid patch targets):\n{bag_sources}"
        f"Produce a surgical patch plan for Sam to apply. Rules:\n"
        f"  1. Describe only targeted, minimal changes — never rewrite whole files.\n"
        f"  2. WRITABLE FILES ONLY: patches may only target 'sam.py' or 'workshop_bench/**/*.py'.\n"
        f"     Never target bag/tests.py, bag/patch_ops.py, or any other bag/ infra file — those are protected and patches to them will be silently rejected.\n"
        f"  3. New standalone logic goes in workshop_bench/. If the idea requires wiring an existing workshop module into the core loop, modifying sam.py is appropriate and encouraged.\n"
        f"  4. For each change, specify EXACTLY:\n"
        f"       - Which file (sam.py or workshop_bench/**/*.py, e.g. workshop_bench/my_folder/foo.py)\n"
        f"       - The operation: replace / insert_after / delete\n"
        f"       - The exact existing string to find ('old' or 'anchor') — copy it CHARACTER-FOR-CHARACTER from the source above, including all whitespace and indentation. Also state the line number it appears on.\n"
        f"       - Keep 'old' and 'anchor' strings as SHORT as possible (1-2 lines max) to reduce whitespace mismatch risk.\n"
        f"       - The new string to substitute or insert\n"
        f"  5. Flag any security or stability risks before listing changes.\n"
        f"  6. If the idea requires no code change this cycle, say so explicitly.\n\n"
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

    # Only append today's idea as a follow-up if it's concrete and not already present.
    # Avoid appending generic placeholders like "Scratchpad" which pollute the queue.
    idea_heading = idea.strip().splitlines()[0].lstrip("#").strip()
    _skip_words = {"scratchpad", "external", "placeholder", "tbd", "n/a", "none"}
    if idea_heading and idea_heading.lower().split()[0] not in _skip_words:
        follow_up = f"Follow-up: {idea_heading[:80]}"
        if follow_up not in goals["next_objectives"]:
            goals["next_objectives"].append(follow_up)

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

    import tracemalloc
    tracemalloc.start()
    _bag_data("cycle_status").write_text("pending")
    log.info("═══════════════════════════════════")
    log.info("  SAM — Operational Cycle Starting ")

    # Initialize core services
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
            log.warning("⚠️  Post-flight failed — attempting self-correction (1 attempt)...")
            # Capture the test output for the corrective prompt
            test_result = subprocess.run(
                [sys.executable, str(TESTS)],
                capture_output=True, text=True, timeout=15, cwd=str(ROOT),
            ) if TESTS.exists() else None
            test_output = (test_result.stdout + test_result.stderr) if test_result else ""

            correction_applied = _behaviour_fix_with_gemini(test_output, plan)

            if correction_applied and self_check() and behaviour_check():
                log.info("✅ Verdict: ACCEPTED after self-correction.")
            else:
                log.error("❌ Verdict: REJECTED. Self-correction did not resolve instability.")
                _cleanup_created_workshop_files()
                _rollback()
                _alert_dot(
                    "Self-modification failed integrity gates. Rolled back for safety.\n\n"
                    f"Plan that caused failure:\n```\n{plan[:800]}\n```\n\n"
                    f"Self-correction attempt {'applied a patch but still failed' if correction_applied else 'produced no patch'}.\n"
                    f"Test output:\n```\n{test_output[:600]}\n```"
                )
                modified = False  # Mark as failed for worklog purposes
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

    # Optional: write an email request for Dot to handle
    goals_fresh = load_goals()   # reload after save
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
