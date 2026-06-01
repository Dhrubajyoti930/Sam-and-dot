"""
bag/workshop.py — Sam's self-organized folder layout under bag/

Sam creates human-friendly folder names (e.g. "My useful tools", "Misc"),
moves existing workshop .py files between folders, and removes obsolete ones.
State is stored in bag/workshop_registry.json.
"""

import json
import re
import shutil
from pathlib import Path

from bag.workshop_paths import (
    BLOCKED_DIR_NAMES,
    is_allowed_workshop_destination,
    is_writable_bag_py,
    iter_writable_bag_py,
    normalize_bag_rel,
    relative_bag_posix,
)

REGISTRY_FILE = "workshop_registry.json"
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


def list_managed_files_for_prompt(bag: Path) -> str:
    lines = [relative_bag_posix(f, bag) for f in iter_writable_bag_py(bag)]
    return "\n".join(f"  - {line}" for line in lines) if lines else "  (none yet)"


def apply_workshop_moves(bag: Path, moves: list, log) -> tuple[list[str], dict[str, str]]:
    """Relocate workshop .py files. Returns (moved paths, path_map old_rel→new_rel)."""
    applied: list[str] = []
    path_map: dict[str, str] = {}
    for op in moves or []:
        if not isinstance(op, dict):
            continue
        src_rel = normalize_bag_rel(op.get("from", ""))
        dst_rel = normalize_bag_rel(op.get("to", ""))
        if not src_rel or not dst_rel or src_rel == dst_rel:
            continue
        src = bag / src_rel
        dst = bag / dst_rel
        if not src.is_file():
            log.warning(f"Move skipped — source missing: bag/{src_rel}")
            continue
        if not is_writable_bag_py(src, bag):
            log.warning(f"Move blocked — source not writable: bag/{src_rel}")
            continue
        if dst.exists():
            log.warning(f"Move skipped — destination exists: bag/{dst_rel}")
            continue
        if not is_allowed_workshop_destination(dst, bag):
            log.warning(f"Move blocked — invalid destination: bag/{dst_rel}")
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        log.info(f"Workshop move: bag/{src_rel} → bag/{dst_rel}")
        applied.append(dst_rel)
        path_map[src_rel] = dst_rel
    return applied, path_map


def _rollback_workshop_moves(bag: Path, path_map: dict[str, str], log):
    for old_rel, new_rel in path_map.items():
        src = bag / new_rel
        dst = bag / old_rel
        if not src.is_file():
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        log.warning(f"Rolled back workshop move: bag/{new_rel} → bag/{old_rel}")


def finalize_workshop_moves(root: Path, bag: Path, path_map: dict[str, str], log) -> bool:
    """Repair imports and verify sam.py + dot.py + bag/ still compile. Roll back on failure."""
    if not path_map:
        return True

    from bag.workshop_imports import (
        apply_import_repairs,
        rewrite_import_paths,
        verify_repo_integrity,
    )

    apply_import_repairs(root, bag, path_map, log)
    if verify_repo_integrity(root, bag, log):
        return True

    log.error("Workshop moves broke repo integrity — rolling back file moves and imports.")
    _rollback_workshop_moves(bag, path_map, log)
    reverse_map = {new: old for old, new in path_map.items()}
    apply_import_repairs(root, bag, reverse_map, log)
    for f in [root / "sam.py", *bag.rglob("*.py")]:
        if not f.exists() or "rollback_registry" in f.parts:
            continue
        try:
            text = f.read_text(encoding="utf-8")
            restored = rewrite_import_paths(text, reverse_map)
            if restored != text:
                f.write_text(restored, encoding="utf-8")
        except OSError:
            pass
    return False


def apply_workshop_deletes(bag: Path, paths: list, log, reason: str = "") -> list[str]:
    """Delete Sam-created workshop .py files. Returns deleted paths (relative to bag/)."""
    deleted = []
    suffix = f" ({reason})" if reason else ""
    for raw in paths or []:
        rel = normalize_bag_rel(raw)
        if not rel:
            continue
        target = bag / rel
        if not target.exists():
            log.warning(f"Delete skipped — not found: bag/{rel}")
            continue
        if not is_writable_bag_py(target, bag):
            log.warning(f"Delete blocked — not writable: bag/{rel}")
            continue
        target.unlink()
        log.info(f"Workshop delete: bag/{rel}{suffix}")
        deleted.append(rel)
    return deleted


def organize_for_cycle(
    bag: Path, idea: str, cycle: int, ask_gemini, log, root: Path | None = None
) -> str:
    """
    Ask Gemini for workshop layout, create folders, move/delete existing files, return target folder.
    """
    reg = load_registry(bag)
    existing = "\n".join(
        f"- {f['name']}: {f.get('purpose', '')}" for f in reg.get("folders", [])
    ) or "(none yet)"
    file_listing = list_managed_files_for_prompt(bag)

    prompt = (
        f"You are Sam organizing your bag/ workshop — folders AND existing files.\n\n"
        f"Cycle: {cycle}\n"
        f"Today's idea (first 500 chars):\n{idea[:500]}\n\n"
        f"Existing folders:\n{existing}\n\n"
        f"Existing Sam-created .py files (paths relative to bag/):\n{file_listing}\n\n"
        f"Respond ONLY with JSON:\n"
        f'  - "folders": list of {{"name": "...", "purpose": "one short line"}}\n'
        f"    Use 3–5 folders total (keep useful existing folders, add new if needed).\n"
        f'    Names: human-readable Title Case with spaces (your own labels, not only examples).\n'
        f'  - "target_folder": folder name for NEW .py modules this cycle\n'
        f'  - "moves": list of {{"from": "path.py", "to": "Folder/path.py"}} to relocate '
        f"EXISTING files listed above into the right folder. Use [] if nothing to move.\n"
        f'  - "deletes": list of paths to remove (obsolete scratch only). Use [] if none.\n\n'
        f"Rules: paths relative to bag/ only; only .py files you created; no governance files; "
        f"no slashes in folder names; max {MAX_NAME_LEN} chars per folder name; "
        f"never move into a path that already exists."
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

    repo_root = root or bag.parent
    moved, path_map = apply_workshop_moves(bag, data.get("moves"), log)
    if moved:
        log.info(f"Workshop reorganized: {len(moved)} file(s) moved.")
        if not finalize_workshop_moves(repo_root, bag, path_map, log):
            log.warning("Workshop moves were rolled back to keep the repo healthy.")

    deleted = apply_workshop_deletes(bag, data.get("deletes"), log, reason="workshop cleanup")
    if deleted:
        log.info(f"Workshop cleanup: {len(deleted)} file(s) deleted.")

    save_registry(bag, reg)
    return reg.get("last_target", "")
