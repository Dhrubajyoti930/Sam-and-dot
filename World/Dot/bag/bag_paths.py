"""
bag/bag_paths.py -- Canonical locations for bag/ files Sam may relocate.

Sam and Dot resolve paths by key (e.g. "experiences") so workshop moves do not
break hardcoded paths. Updated automatically when workshop.py moves files.
"""

import json
from pathlib import Path

REGISTRY_NAME = "workshop_registry.json"

# Default location relative to bag/ (posix). Only governance + infra stay fixed elsewhere.
DEFAULT_LOCATIONS = {
    "idea_of_day": "../../Sam/My_memories/IDEA_OF_THE_DAY.md",
    "experiences": "../../Sam/My_memories/experiences.json",
    "request": "../../Sam/My_memories/request.json",
    "cycle_status": "../../Sam/My_memories/cycle_status.txt",
    "prompt_patch": "../../Sam/My_memories/prompt_patch.json",
    "worklog": "../../Sam/My_memories/worklog.json",
    "sent_emails": "../../Sam/My_memories/sent_emails.json",
}

# basename -> registry key (for move tracking)
_BASENAME_TO_KEY = {Path(v).name: k for k, v in DEFAULT_LOCATIONS.items()}


def _registry_path(bag: Path) -> Path:
    return bag / REGISTRY_NAME


def load_locations(bag: Path) -> dict:
    path = _registry_path(bag)
    if not path.exists():
        return dict(DEFAULT_LOCATIONS)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return dict(DEFAULT_LOCATIONS)
    locs = dict(DEFAULT_LOCATIONS)
    stored = data.get("file_locations") or {}
    for key in DEFAULT_LOCATIONS:
        if key in stored and stored[key]:
            locs[key] = str(stored[key]).replace("\\", "/").lstrip("/")
    return locs


def save_locations(bag: Path, locations: dict):
    path = _registry_path(bag)
    data = {}
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            data = {}
    data["file_locations"] = {
        k: locations[k] for k in DEFAULT_LOCATIONS if locations.get(k)
    }
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def resolve(bag: Path, key: str) -> Path:
    if key not in DEFAULT_LOCATIONS:
        raise KeyError(f"Unknown bag path key: {key}")
    locs = load_locations(bag)
    return bag / locs[key]


def apply_move_map(bag: Path, path_map: dict[str, str], log=None) -> None:
    """After workshop moves, persist new relative paths for tracked files."""
    if not path_map:
        return
    locs = load_locations(bag)
    updated = []
    for old_rel, new_rel in path_map.items():
        key = _BASENAME_TO_KEY.get(Path(old_rel).name)
        if not key:
            continue
        locs[key] = new_rel.replace("\\", "/").lstrip("/")
        updated.append(f"{key}->{locs[key]}")
    if updated:
        save_locations(bag, locs)
        if log:
            log.info(f"bag_paths updated: {', '.join(updated)}")
