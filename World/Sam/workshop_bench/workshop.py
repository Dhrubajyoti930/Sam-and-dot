"""
bag/workshop.py — Sam's life-like layout under bag/

Sam keeps personal data in home/, and organizes code across folders like
school/, my toys/, my friend/, and my gadgets/. Platform files at bag/ root
and everything under home/ never move via workshop.
"""

import json
import re
import shutil
from pathlib import Path

from bag.workshop_paths import (
    BLOCKED_DIR_NAMES,
    DEFAULT_LIFE_FOLDERS,
    HOME_ROOT,
    IMMUTABLE_BASENAMES,
    is_allowed_workshop_destination,
    is_movable_bag_file,
    iter_movable_bag_files,
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
    return (name[:MAX_NAME_LEN] if name else "my toys")


def is_allowed_workshop_dir(name: str) -> bool:
    safe = sanitize_folder_name(name)
    return safe not in BLOCKED_DIR_NAMES and safe.lower() != REGISTRY_FILE.replace(".json", "")


def ensure_folder(bag: Path, name: str, purpose: str = "", cycle: int = 0) -> Path:
    safe = sanitize_folder_name(name)
    if not is_allowed_workshop_dir(safe) or safe == HOME_ROOT:
        safe = "my toys"
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
        return "  (no life folders yet — use home, school, my toys, my friend, my gadgets)\n"
    target = reg.get("last_target", "")
    block = "\n".join(lines) + "\n"
    if target and target != HOME_ROOT:
        block += f"Preferred folder for NEW code this cycle: bag/{target}/\n"
    block += f"Personal data stays in bag/{HOME_ROOT}/ (do not move those files).\n"
    return block


def list_managed_files_for_prompt(bag: Path) -> str:
    lines = [relative_bag_posix(f, bag) for f in iter_movable_bag_files(bag)]
    return "\n".join(f"  - {line}" for line in lines) if lines else "  (none yet)"


def infer_default_moves(bag: Path, target_folder: str) -> list[dict]:
    """
    When Gemini returns no moves, relocate workshop files not already under target_folder.
    Preserves each file's basename (e.g. Misc/foo.py → Target/foo.py).
    """
    target = sanitize_folder_name(target_folder)
    if not target:
        return []

    moves = []
    for f in iter_movable_bag_files(bag):
        rel = relative_bag_posix(f, bag)
        parts = Path(rel).parts
        if len(parts) >= 2 and parts[0] == target:
            continue
        if len(parts) == 1 and parts[0] == target:
            continue
        dst = f"{target}/{parts[-1]}"
        if rel != dst:
            moves.append({"from": rel, "to": dst})
    return moves


def _parse_workshop_json(raw: str, log) -> dict:
    if not raw or raw.strip().startswith("[Gemini error:"):
        log.warning("Workshop layout: invalid Gemini response — cannot parse JSON.")
        return {}
    clean = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        return json.loads(clean)
    except Exception as e:
        log.warning(f"Workshop layout JSON parse failed: {e} — raw starts: {clean[:120]!r}")
        return {}


def apply_workshop_moves(bag: Path, moves: list, log) -> tuple[list[str], dict[str, str]]:
    """Relocate movable bag/ files (any type). Returns (moved paths, path_map old_rel→new_rel)."""
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
        if not is_movable_bag_file(src, bag):
            log.warning(f"Move blocked — immutable or protected: bag/{src_rel}")
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

    if any(rel.endswith(".py") for rel in path_map.values()):
        apply_import_repairs(root, bag, path_map, log)
    if verify_repo_integrity(root, bag, log):
        from bag.bag_paths import apply_move_map

        apply_move_map(bag, path_map, log)
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
    """Delete movable bag/ files. Returns deleted paths (relative to bag/)."""
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
        if not is_movable_bag_file(target, bag):
            log.warning(f"Delete blocked — immutable or protected: bag/{rel}")
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
        f"You are Sam tidying your bag/ — like real life: home, school, my toys, my friend, my gadgets.\n\n"
        f"Cycle: {cycle}\n"
        f"Today's idea (first 500 chars):\n{idea[:500]}\n\n"
        f"Existing folders:\n{existing}\n\n"
        f"Existing movable files in bag/ (paths relative to bag/; you may reorganize these):\n"
        f"{file_listing}\n\n"
        f"Never move or delete (governance/infra): {', '.join(sorted(IMMUTABLE_BASENAMES))}\n"
        f"Never move anything under bag/{HOME_ROOT}/ — memories and daily files live there.\n\n"
        f"Respond ONLY with JSON:\n"
        f'  - "folders": list of {{"name": "...", "purpose": "one short line"}}\n'
        f'    Prefer life-like names: home, school, my toys, my friend, my gadgets (spaces OK).\n'
        f'    Do not use "{HOME_ROOT}" as target_folder for new code.\n'
        f'  - "target_folder": where NEW .py modules belong (e.g. "my toys")\n'
        f'  - "moves": list of {{"from": "path", "to": "my gadgets/tool.py"}} — tidy code into life folders. '
        f"Use [] only if already organized.\n"
        f'  - "deletes": list of paths to remove (obsolete only). Use [] if none.\n\n'
        f"Rules: paths relative to bag/ only; no immutable files; "
        f"no slashes in folder names; max {MAX_NAME_LEN} chars per folder name; "
        f"never move into a path that already exists."
    )

    raw = ask_gemini(prompt)
    data = _parse_workshop_json(raw, log)

    folders = data.get("folders") or []
    if not folders and not reg.get("folders"):
        folders = [
            {"name": name, "purpose": {
                "home": "My memories, diary, and daily files",
                "school": "What I am learning",
                "my toys": "Fun experiments and playful code",
                "my friend": "Things for Dot and people I care about",
                "my gadgets": "Useful tools and helpers",
            }.get(name, "Sam's place")}
            for name in DEFAULT_LIFE_FOLDERS
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
    if target and target != HOME_ROOT:
        ensure_folder(bag, target, "", cycle)
        reg["last_target"] = target
        log.info(f"Workshop target folder for cycle {cycle}: bag/{target}/")
    elif reg["folders"]:
        fallback = next(
            (f["name"] for f in reg["folders"] if f.get("name") != HOME_ROOT),
            "my toys",
        )
        reg["last_target"] = fallback
        target = fallback

    repo_root = root or bag.parent
    moves = data.get("moves")
    if moves is None:
        moves = []
    if not moves and list_managed_files_for_prompt(bag) != "  (none yet)":
        moves = infer_default_moves(bag, target)
        if moves:
            log.info(
                f"Workshop: Gemini proposed no moves — applying {len(moves)} default move(s) "
                f"into bag/{target}/."
            )

    moved, path_map = apply_workshop_moves(bag, moves, log)
    if moved:
        log.info(f"Workshop reorganized: {len(moved)} file(s) moved.")
        if not finalize_workshop_moves(repo_root, bag, path_map, log):
            log.warning("Workshop moves were rolled back to keep the repo healthy.")

    deleted = apply_workshop_deletes(bag, data.get("deletes"), log, reason="workshop cleanup")
    if deleted:
        log.info(f"Workshop cleanup: {len(deleted)} file(s) deleted.")

    save_registry(bag, reg)
    return reg.get("last_target", "")
