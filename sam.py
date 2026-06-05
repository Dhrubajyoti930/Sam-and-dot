"""
sam.py
Sam — the creative AI agent.
Pure orchestration. All logic lives in _starter_pack.py.
Workflow: get idea → decide script → run existing OR plan → build → run
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from modules._starter_pack import (
    _get_or_generate_idea,
    _decide_script,
    _run_script,
    _make_plan,
    _ensure_modules_exist,
    _execute_plan,
    _save_script,
    _call_delay,
)
from modules import get_module_taglines, get_script_taglines

GEM_KEY     = os.environ.get("GEM_KEY_SAM") or os.environ.get("SPARE_KEY")
IDEA_QUEUE  = "idea_queue.json"
SCRIPTS_DIR = "scripts"
MODULES_DIR = "modules"


def main():
    print("[Sam] Waking up...")

    idea = _get_or_generate_idea(IDEA_QUEUE, GEM_KEY)
    print(f"[Sam] Working on: {idea}")

    script_taglines = get_script_taglines()
    module_taglines = get_module_taglines()

    # try to find an existing script that fits
    if script_taglines:
        chosen = _decide_script(idea, script_taglines, GEM_KEY)
        chosen_path = os.path.join(SCRIPTS_DIR, chosen)
        if chosen != "none" and os.path.exists(chosen_path):
            print(f"[Sam] Running existing script: {chosen}")
            stdout, stderr, _ = _run_script(chosen_path)
            print(f"[Sam] Output:\n{stdout}")
            if stderr:
                print(f"[Sam] Errors:\n{stderr}")
            return

    # nothing fits — build a new script
    print("[Sam] Building a new script...")
    fallback = ["s_example: demo module showing Sam conventions"]
    plan = _make_plan(idea, module_taglines or fallback, GEM_KEY)
    print(f"[Sam] Plan ready: {plan['script_name']}")

    _ensure_modules_exist(plan, MODULES_DIR, GEM_KEY)
    _call_delay(1)

    code = _execute_plan(plan, GEM_KEY)
    script_path = _save_script(plan, code, SCRIPTS_DIR, GEM_KEY)

    stdout, stderr, _ = _run_script(script_path)
    print(f"[Sam] Output:\n{stdout}")
    if stderr:
        print(f"[Sam] Errors:\n{stderr}")

    print("[Sam] Done.")


if __name__ == "__main__":
    main()
