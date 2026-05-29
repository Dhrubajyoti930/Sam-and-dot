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
import asyncio
import re
import sys
import json
import time
import datetime
import logging
import logging.handlers
import subprocess
import traceback
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
from google import genai
from bag.async_batch import AsyncWorkerPool

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
    for attempt in range(retries):
        try:
            response = CLIENT.models.generate_content(
                model=MODEL,
                contents=prompt,
            )
            return response.text.strip()
        except Exception as e:
            err = str(e)
            if "429" in err or "503" in err or "UNAVAILABLE" in err or "RESOURCE_EXHAUSTED" in err:
                wait = _CALL_DELAY * (2 ** attempt)
                log.warning(f"Gemini transient error (attempt {attempt+1}): {e}. Retrying in {wait}s.")
                time.sleep(wait)
            elif "404" in err:
                log.critical("MODEL STRING MAY BE DEPRECATED — owner intervention required.")
                _alert_dot("Gemini returned 404. The model string may be deprecated. Owner must update MODEL in sam.py and bag/dot.py.")
                return f"[Gemini error: model not found]"
            else:
                log.error(f"Gemini call failed (non-retryable): {e}")
                return f"[Gemini error: {e}]"
    log.error("Gemini call failed after all retries.")
    return "[Gemini error: exhausted retries]"


def _sleep():
    """Pause between Gemini calls to respect RPM limits."""
    time.sleep(_CALL_DELAY)


def snapshot_sam() -> Path:
    """Archive current sam.py into rollback_registry with a timestamp."""
    ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    dest = ROLLBACK_REG / f"sam_{ts}.py"
    dest.write_text(Path(__file__).read_text())
    log.info(f"Snapshot saved → {dest.name}")
    # ── Prune old snapshots — keep only the 20 most recent ──
    snapshots = sorted(ROLLBACK_REG.glob("sam_*.py"), reverse=True)
    for old in snapshots[20:]:
        old.unlink()
        log.info(f"Pruned old snapshot → {old.name}")
    return dest


def self_check() -> bool:
    """Boot-time integrity check. Returns True if healthy, triggers rollback if not."""
    try:
        result = subprocess.run(
            [sys.executable, "-c",
             f"import py_compile; py_compile.compile('{__file__}', doraise=True)"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            log.error("Syntax check failed — initiating rollback.")
            _rollback()
            return False
        return True
    except Exception as e:
        log.error(f"Self-check exception: {e}")
        return False


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
    """Pull the most recent healthy sam.py from the rollback registry."""
    snapshots = sorted(ROLLBACK_REG.glob("sam_*.py"), reverse=True)
    if not snapshots:
        log.critical("No snapshots in rollback_registry — cannot recover.")
        return
    latest = snapshots[0]
    Path(__file__).write_text(latest.read_text())
    log.warning(f"Rolled back to {latest.name}")


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
        f"  - If no concrete changes are needed, return an empty array []."
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
    who_i_am   = load_who_i_am()
    personality = load_personality()

    _sleep()
    prompt = (
        f"You are Sam, an autonomous developer who continuously improves himself.\n\n"
        f"Character:\n{personality}\n\n"
        f"Market signals this cycle:\n{market_data}\n\n"
        f"Skill learned this cycle:\n{skill}\n\n"
        f"Current architecture overview:\n{who_i_am}\n\n"
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

    who_i_am    = load_who_i_am()
    personality = load_personality()
    sam_src     = Path(__file__).read_text()

    _sleep()
    prompt = (
        f"You are Sam's Gemini refactoring assistant.\n\n"
        f"Sam's character:\n{personality}\n\n"
        f"Dot's guidance (motion.md — read carefully):\n{motion_content}\n\n"
        f"Today's development idea:\n{idea}\n\n"
        f"Sam's current sam.py (full source):\n```python\n{sam_src}\n```\n\n"
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
        f"Name ONE specific, honest 1%-growth metric for this cycle. "
        f"It must be precise and reflect what actually happened — not a generic phrase. "
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
        f"Decide: Is there a specific tech company, open-source maintainer, or indie developer "
        f"it would be genuinely valuable to reach out to about this idea or to learn from? "
        f"Reply ONLY with a JSON object:\n"
        f"  - 'should_email': true or false\n"
        f"  - 'intent': if true, 1-2 sentences on what Sam wants to communicate\n"
        f"  - 'target_description': if true, describe who — e.g. 'maintainer of LangChain on GitHub'\n"
        f"  - 'tone': 'professional' or 'friendly'\n"
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
    log.info(f"request.json written — Dot will handle sending.")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN LOOP
# ═══════════════════════════════════════════════════════════════════════════════

def run_cycle():
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

    # Self-modification — snapshot first, then apply, then verify
    snapshot_sam()
    if apply_self_modification(plan):
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

    # Phase VI — prompt evolution
    evolution = phase_vi_cognitive_evolution(goals)

    # Phase VII — state persistence (also appends to experiences.json)
    phase_vii_state_saving(goals, skill, idea, plan, evolution)

    # Optional: write an email request for Dot to handle
    goals_fresh = load_goals()   # reload after save
    maybe_write_email_request(idea, goals_fresh)

    log.info("Cycle complete.")


if __name__ == "__main__":
    run_cycle()
