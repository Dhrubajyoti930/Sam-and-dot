"""
bag/workshop.py — Sam's self-organized folder layout under bag/

Sam creates human-friendly folder names (e.g. "My useful tools", "Misc").
State is stored in bag/workshop_registry.json.
"""

import json
import re
from pathlib import Path

REGISTRY_FILE = "workshop_registry.json"
BLOCKED_DIR_NAMES = frozenset({"rollback_registry", "__pycache__", ".git"})
MAX_NAME_LEN = 56


def _registry_path(bag: Path) -> Path:
    return bag / REGISTRY_FILE


def load_registry(bag: Path) -> dict:
    path = _registry_path(bag)
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"folders": [], "last_target": ""}


def save_registry(bag: Path, data: dict):
    _registry_path(bag).write_text(json.dumps(data, indent=2), encoding="utf-8")


def sanitize_folder_name(name: str) -> str:
    name = (name or "").strip().strip("/\\")
    name = re.sub(r'[<>:"|?*]', "", name)
    name = re.sub(r"\s+", " ", name)
    return (name[:MAX_NAME_LEN] if name else "Misc")


def is_allowed_workshop_dir(name: str) -> bool:
    safe = sanitize_folder_name(name)
    return safe not in BLOCKED_DIR_NAMES and safe.lower() != REGISTRY_FILE.replace(".json", "")


def ensure_folder(bag: Path, name: str, purpose: str = "", cycle: int = 0) -> Path:
    safe = sanitize_folder_name(name)
    if not is_allowed_workshop_dir(safe):
        safe = "Misc"
    folder = bag / safe
    folder.mkdir(parents=True, exist_ok=True)

    reg = load_registry(bag)
    folders = reg.get("folders", [])
    if not any(f.get("name") == safe for f in folders):
        folders.append({
            "name": safe,
            "purpose": purpose or "Sam-created workshop folder",
            "created_cycle": cycle,
        })
    reg["folders"] = folders
    save_registry(bag, reg)
    return folder


def format_layout_for_prompt(bag: Path) -> str:
    reg = load_registry(bag)
    lines = []
    for entry in reg.get("folders", []):
        name = entry.get("name", "")
        purpose = entry.get("purpose", "")
        lines.append(f"  - bag/{name}/ — {purpose}")
    if not lines:
        return "  (no workshop folders yet — create 3–5 with clear names this cycle)\n"
    target = reg.get("last_target", "")
    block = "\n".join(lines) + "\n"
    if target:
        block += f"Preferred folder for NEW modules this cycle: bag/{target}/\n"
    return block


def organize_for_cycle(bag: Path, idea: str, cycle: int, ask_gemini, log) -> str:
    """
    Ask Gemini for workshop folder names (Sam's own labels), create them, return target folder.
    """
    reg = load_registry(bag)
    existing = "\n".join(
        f"- {f['name']}: {f.get('purpose', '')}" for f in reg.get("folders", [])
    ) or "(none yet)"

    prompt = (
        f"You are Sam organizing your bag/ workshop with friendly folder names.\n\n"
        f"Cycle: {cycle}\n"
        f"Today's idea (first 500 chars):\n{idea[:500]}\n\n"
        f"Existing folders:\n{existing}\n\n"
        f"Respond ONLY with JSON:\n"
        f'  - "folders": list of {{"name": "...", "purpose": "one short line"}}\n'
        f'    Use 3–5 folders total (include existing ones you want to keep, add new if needed).\n'
        f'    Names must be human-readable Title Case with spaces, e.g. "My useful tools", '
        f'"My ongoing projects", "Misc" — but pick names that fit YOUR work, not these examples only.\n'
        f'  - "target_folder": which folder name new Python modules should go in THIS cycle\n\n'
        f"Rules: no slashes in names, no governance file names, max {MAX_NAME_LEN} chars per name."
    )

    raw = ask_gemini(prompt)
    try:
        clean = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        data = json.loads(clean)
    except Exception as e:
        log.warning(f"Workshop layout JSON parse failed: {e} — using defaults.")
        data = {}

    folders = data.get("folders") or []
    if not folders and not reg.get("folders"):
        folders = [
            {"name": "My useful tools", "purpose": "Reusable helpers and small utilities"},
            {"name": "My ongoing projects", "purpose": "Active multi-cycle experiments"},
            {"name": "Misc", "purpose": "One-off prototypes and scratch code"},
        ]

    reg["folders"] = []
    for entry in folders:
        name = entry.get("name", "")
        purpose = entry.get("purpose", "")
        if not name:
            continue
        ensure_folder(bag, name, purpose, cycle)
        reg["folders"].append({
            "name": sanitize_folder_name(name),
            "purpose": purpose,
            "created_cycle": entry.get("created_cycle", cycle),
        })

    target = sanitize_folder_name(data.get("target_folder", "") or "")
    if not target and reg["folders"]:
        target = reg["folders"][0]["name"]
    if target:
        ensure_folder(bag, target, "", cycle)
        reg["last_target"] = target
        log.info(f"Workshop target folder for cycle {cycle}: bag/{target}/")

    save_registry(bag, reg)
    return reg.get("last_target", "")
