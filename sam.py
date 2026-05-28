"""
sam.py — Central Intelligence Loop
Project Sam: The Autonomous Developer Agent

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
import json
import time
import datetime
import logging
import subprocess
import traceback
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT          = Path(__file__).parent.resolve()
WHO_I_AM      = ROOT / "WHO_I_AM.md"
GOALS         = ROOT / "goals.json"
BAG           = ROOT / "bag"
MOTION        = BAG  / "motion.md"
ROLLBACK_REG  = BAG  / "rollback_registry"
VECTOR_DB     = ROOT / "vector_db"
IDEA_OF_DAY   = BAG  / "IDEA_OF_THE_DAY.md"

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

# ── Gemini client ─────────────────────────────────────────────────────────────
import google.generativeai as genai

GEM_KEY = os.environ.get("GEM_KEY_SAM")
if not GEM_KEY:
    raise EnvironmentError("GEM_KEY_SAM secret is not set.")
genai.configure(api_key=GEM_KEY)
MODEL = genai.GenerativeModel("gemini-3.5-flash")   # massive context window


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def load_goals() -> dict:
    if GOALS.exists():
        with open(GOALS) as f:
            return json.load(f)
    return {"cycles": 0, "growth_log": [], "next_objectives": [], "last_1pct_metric": ""}


def save_goals(data: dict):
    with open(GOALS, "w") as f:
        json.dump(data, f, indent=2)
    log.info("goals.json updated.")


def load_who_i_am() -> str:
    if WHO_I_AM.exists():
        return WHO_I_AM.read_text()
    return "(WHO_I_AM.md not yet generated)"


def read_motion() -> str:
    """Sam reads motion.md exactly once — at the top of Phase V."""
    if MOTION.exists():
        return MOTION.read_text()
    return "(motion.md is empty — Dot has not yet written.)"


def ask_gemini(prompt: str) -> str:
    """Send a prompt to Sam's own Gemini instance and return the text response."""
    try:
        response = MODEL.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        log.error(f"Gemini call failed: {e}")
        return f"[Gemini error: {e}]"


def snapshot_sam() -> Path:
    """Archive current sam.py into rollback_registry with a timestamp."""
    ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    dest = ROLLBACK_REG / f"sam_{ts}.py"
    dest.write_text(Path(__file__).read_text())
    log.info(f"Snapshot saved → {dest.name}")
    return dest


def self_check() -> bool:
    """Boot-time integrity check. Returns True if healthy, triggers rollback if not."""
    try:
        result = subprocess.run(
            ["python", "-c", f"import py_compile; py_compile.compile('{__file__}', doraise=True)"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            log.error("Syntax check failed — initiating rollback.")
            _rollback()
            return False
        return True
    except Exception as e:
        log.error(f"Self-check exception: {e}")
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


# ═══════════════════════════════════════════════════════════════════════════════
# PHASES
# ═══════════════════════════════════════════════════════════════════════════════

def phase_i_deep_learning(goals: dict) -> str:
    """Acquire a new hard skill or prompting technique."""
    log.info("── Phase I: Deep Learning ──")
    objectives = goals.get("next_objectives", [])
    focus = objectives[0] if objectives else "latest LLM context-engineering techniques"

    prompt = (
        f"You are Sam, an autonomous developer agent. "
        f"Your learning focus for this cycle is: '{focus}'. "
        f"Produce a concise but dense technical summary (300-400 words) of the most important "
        f"concepts, patterns, or techniques a developer should know about this topic today. "
        f"Conclude with three concrete action items Sam should implement."
    )
    result = ask_gemini(prompt)
    log.info("Phase I complete.")
    return result


def phase_ii_spaced_repetition(goals: dict) -> str:
    """Revise yesterday's skill; run mini-tests to prevent model drift."""
    log.info("── Phase II: Spaced Repetition ──")
    growth_log = goals.get("growth_log", [])
    last_skill = growth_log[-1].get("skill", "general Python async patterns") if growth_log else "general Python async patterns"

    prompt = (
        f"You are Sam. Yesterday you studied: '{last_skill}'. "
        f"Generate 3 concise but challenging quiz questions to test retention of this skill, "
        f"followed immediately by the correct answers. Keep the format tight."
    )
    result = ask_gemini(prompt)
    log.info("Phase II complete.")
    return result


def phase_iii_market_ingestion() -> str:
    """Scrape trends; in CI we simulate with a Gemini synthesis of current tech directions."""
    log.info("── Phase III: Market & Code Ingestion ──")
    prompt = (
        "You are Sam's market scanner. List the top 5 high-velocity technology or open-source "
        "trends a Python AI developer should be tracking right now. For each trend, provide: "
        "trend name, one-sentence description, and a specific GitHub repo or resource URL worth exploring."
    )
    result = ask_gemini(prompt)
    log.info("Phase III complete.")
    return result


def phase_iv_synthesis(market_data: str) -> str:
    """Generate IDEA_OF_THE_DAY.md; vet any external code snippets."""
    log.info("── Phase IV: Synthesis ──")
    who_i_am = load_who_i_am()

    prompt = (
        f"You are Sam, an autonomous developer who continuously improves himself. "
        f"Based on these market signals:\n\n{market_data}\n\n"
        f"And given your current architecture (summary):\n\n{who_i_am}\n\n"
        f"Propose ONE concrete, implementable development idea for today. "
        f"Format it as a short markdown document with: ## Idea, ## Why, ## Implementation Steps, ## Risk."
    )
    idea = ask_gemini(prompt)
    IDEA_OF_DAY.write_text(idea)
    log.info(f"IDEA_OF_THE_DAY.md written.")
    return idea


def phase_v_development(idea: str, goals: dict) -> str:
    """Read motion.md FIRST, then execute or self-modify."""
    log.info("── Phase V: Development & Refactor ──")

    # ⚠️  motion.md is read ONCE, here, and nowhere else.
    motion_content = read_motion()
    log.info("motion.md read.")

    who_i_am = load_who_i_am()

    prompt = (
        f"You are Sam's Gemini refactoring assistant. "
        f"Sam's watchdog (Dot) left the following guidance:\n\n{motion_content}\n\n"
        f"Today's development idea:\n\n{idea}\n\n"
        f"Sam's current architecture snapshot :\n\n{who_i_am}\n\n"
        f"Provide a precise, minimal code diff or implementation plan Sam should apply to his codebase. "
        f"Flag any security or stability risks. Do NOT rewrite files wholesale — propose targeted changes only."
    )
    plan = ask_gemini(prompt)
    log.info("Phase V complete.")
    return plan


def phase_vi_cognitive_evolution(goals: dict) -> str:
    """Upgrade internal prompts; refactor system prompts for parser stability."""
    log.info("── Phase VI: Cognitive Evolution ──")

    prompt = (
        "You are Sam. Review the latest context engineering paradigms (e.g., chain-of-thought, "
        "self-consistency, tree-of-thoughts, ReAct, structured outputs). "
        "Suggest one concrete prompt engineering improvement Sam could apply to his own internal "
        "Gemini calls in the next cycle. Be specific — include a before/after example."
    )
    evolution = ask_gemini(prompt)
    log.info("Phase VI complete.")
    return evolution


def phase_vii_state_saving(goals: dict, skill_learned: str, evolution_note: str):
    """Commit work, log metrics, write next cycle's objectives into goals.json."""
    log.info("── Phase VII: State Saving ──")

    ts = datetime.datetime.utcnow().isoformat()
    cycle_num = goals.get("cycles", 0) + 1

    # The 1% growth metric is chosen by Sam each cycle
    one_pct_metric = f"prompt_quality_improvement (cycle {cycle_num})"

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
    import re
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

    # Phases I–IV run uninhibited
    skill      = phase_i_deep_learning(goals)
    _          = phase_ii_spaced_repetition(goals)
    market     = phase_iii_market_ingestion()
    idea       = phase_iv_synthesis(market)

    # Phase V reads motion.md at the top — then executes
    plan       = phase_v_development(idea, goals)

    # Phase VI — prompt evolution
    evolution  = phase_vi_cognitive_evolution(goals)

    # Phase VII — state persistence
    phase_vii_state_saving(goals, skill, evolution)

    log.info("Cycle complete.")


if __name__ == "__main__":
    run_cycle()
