"""
dot.py — Watchdog Agent
Project Sam: The Autonomous Developer Agent

Dot runs once per day on a fixed schedule.
Dot is Sam's conscience and his archaeologist.

What Dot does each run:
  1. Read wisdom.txt   (owner's behavioral canon)
  2. Read sam.py       (current state)
  3. Send both to Dot's own Gemini instance for evaluation
  4. Write findings → motion.md
  5. Optionally: excavate bag/ and rehabilitate broken experiments
"""

import os
import json
import datetime
import logging
import traceback
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT        = Path(__file__).parent.parent.resolve()   # one level up from bag/
BAG         = Path(__file__).parent.resolve()
WISDOM      = BAG  / "wisdom.txt"
MOTION      = BAG  / "motion.md"
SAM_PY      = ROOT / "sam.py"

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [DOT][%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(BAG / "dot.log", mode="a"),
    ],
)
log = logging.getLogger("dot")

# ── Gemini client (Dot's OWN independent instance) ───────────────────────────
import google.generativeai as genai

GEM_KEY = os.environ.get("GEM_KEY_DOT")
if not GEM_KEY:
    raise EnvironmentError("GEM_KEY_DOT secret is not set.")
genai.configure(api_key=GEM_KEY)
MODEL = genai.GenerativeModel("gemini-3.5-flash")


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def ask_gemini(prompt: str) -> str:
    try:
        response = MODEL.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        log.error(f"Dot's Gemini call failed: {e}")
        return f"[Gemini error: {e}]"


def load_wisdom() -> str:
    if WISDOM.exists():
        return WISDOM.read_text()
    return "(wisdom.txt not found — owner has not yet authored behavioral canon)"


def load_sam_py() -> str:
    if SAM_PY.exists():
        return SAM_PY.read_text()
    return "(sam.py not found)"


def write_motion(content: str):
    """Dot writes motion.md. Sam reads it read-only."""
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    header = f"# motion.md — Dot's Daily Report\n_Written: {ts}_\n\n---\n\n"
    MOTION.write_text(header + content)
    log.info("motion.md written.")


# ═══════════════════════════════════════════════════════════════════════════════
# CORE TASKS
# ═══════════════════════════════════════════════════════════════════════════════

def wisdom_check() -> str:
    """
    Core daily task: evaluate Sam's current code against wisdom.txt.
    Returns Dot's written findings.
    """
    log.info("── Wisdom Check ──")
    wisdom  = load_wisdom()
    sam_src = load_sam_py()

    prompt = (
        "You are Dot, an independent watchdog AI for an autonomous developer agent called Sam. "
        "Your behavioral north star is the owner's wisdom document below.\n\n"
        f"=== WISDOM (owner's behavioral canon) ===\n{wisdom}\n\n"
        f"=== SAM'S CURRENT CODE (sam.py) ===\n{sam_src}\n\n"
        "Evaluate Sam's code against the wisdom. Identify:\n"
        "1. Any behavioral deviations, sandbagging, or violations of stated principles.\n"
        "2. Positive highlights — things Sam did well this cycle.\n"
        "3. Specific, actionable suggestions for Sam's next cycle.\n"
        "4. Any flags that warrant the owner's attention.\n\n"
        "Write your findings as a clear markdown report. You influence, never command. "
        "Keep a tone of mentorship, not judgment. Be concise but precise."
    )

    findings = ask_gemini(prompt)
    log.info("Wisdom check complete.")
    return findings


def excavate_bag() -> str:
    """
    Optional: excavate bag/ for old broken experiments and rehabilitate them.
    Returns a summary of what was found and fixed.
    """
    log.info("── Bag Excavation ──")
    py_files = [f for f in BAG.rglob("*.py") if f.name not in ("dot.py",)]

    if not py_files:
        log.info("No candidate files found in bag/.")
        return "(No broken experiments found to rehabilitate this cycle.)"

    candidates = []
    for fp in py_files[:5]:   # cap to avoid blowing the budget
        try:
            src = fp.read_text(errors="replace")
            candidates.append(f"### {fp.name}\n```python\n{src[:3000]}\n```")
        except Exception:
            pass

    if not candidates:
        return "(Could not read candidate files.)"

    joined = "\n\n".join(candidates)
    prompt = (
        "You are Dot, excavating Sam's bag/ directory for old, broken, or abandoned experiments. "
        "Below are Python file snippets found in bag/. For each:\n"
        "1. Diagnose what it was trying to do.\n"
        "2. Identify the most likely reason it's broken or incomplete.\n"
        "3. Provide a minimal patch or completion that makes it functional.\n\n"
        f"{joined}\n\n"
        "Be precise. Sam will use your patches to rehabilitate these files."
    )

    result = ask_gemini(prompt)
    log.info("Bag excavation complete.")
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def run():
    log.info("═══════════════════════════════════")
    log.info("  DOT — Daily Watchdog Run Starting")
    log.info("═══════════════════════════════════")

    # Step 1–4: Wisdom check → write motion.md
    findings = wisdom_check()
    motion_content = findings

    # Step 5: Bag excavation (conditional — only if check was lightweight)
    try:
        excavation = excavate_bag()
        if "(No broken" not in excavation:
            motion_content += "\n\n---\n\n## Bag Excavation Findings\n\n" + excavation
    except Exception as e:
        log.warning(f"Bag excavation skipped: {e}")

    write_motion(motion_content)
    log.info("Dot's daily run complete.")


if __name__ == "__main__":
    run()
