"""
bag/workshop.py â€” Sam's craft organization under workshop_bench/
"""

import json
import re
import shutil
from pathlib import Path

from bag.workshop_paths import (
    BLOCKED_DIR_NAMES,
    WORKSHOP_ROOT,
    is_movable_bag_file,
    iter_movable_bag_files,
    relative_posix,
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


def ensure_folder(workshop: Path, bag: Path, name: str, purpose: str = "", cycle: int = 0) -> Path:
    safe = sanitize_folder_name(name)
    if not is_allowed_workshop_dir(safe):
        safe = "my toys"
    folder = workshop / safe
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


def format_layout_for_prompt(workshop: Path) -> str:
    # We can just list actual subfolders in workshop_bench
    folders = [d for d in workshop.iterdir() if d.is_dir() and d.name not in BLOCKED_DIR_NAMES]
    if not folders:
        return f"  (no folders yet in {WORKSHOP_ROOT}/ â€” you may create some)\n"

    lines = []
    for d in folders:
        lines.append(f"  - {WORKSHOP_ROOT}/{d.name}/")
    return "\n".join(lines) + "\n"


def list_managed_files_for_prompt(workshop: Path) -> str:
    lines = [relative_posix(f, workshop) for f in iter_movable_bag_files(workshop)]
    return "\n".join(f"  - {line}" for line in lines) if lines else "  (none yet)"


def infer_default_moves(workshop: Path, target_folder: str) -> list[dict]:
    target = sanitize_folder_name(target_folder)
    if not target:
        return []

    moves = []
    for f in iter_movable_bag_files(workshop):
        rel = relative_posix(f, workshop)
        parts = Path(rel).parts
        if len(parts) >= 2 and parts[0] == target:
            continue
        dst = f"{target}/{parts[-1]}"
        if rel != dst:
            moves.append({"from": rel, "to": dst})
    return moves


def apply_workshop_moves(workshop: Path, moves: list, log) -> tuple[list[str], dict[str, str]]:
    applied: list[str] = []
    path_map: dict[str, str] = {}
    for op in moves or []:
        if not isinstance(op, dict):
            continue
        src_rel = op.get("from", "").replace("\\", "/").strip("/")
        dst_rel = op.get("to", "").replace("\\", "/").strip("/")
        if not src_rel or not dst_rel or src_rel == dst_rel:
            continue
        src = workshop / src_rel
        dst = workshop / dst_rel
        if not src.is_file():
            continue
        if not is_movable_bag_file(src, workshop):
            continue
        if dst.exists():
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        log.info(f"Workshop move: {WORKSHOP_ROOT}/{src_rel} â†’ {WORKSHOP_ROOT}/{dst_rel}")
        applied.append(dst_rel)
        path_map[src_rel] = dst_rel
    return applied, path_map


def finalize_workshop_moves(sam_root: Path, workshop: Path, bag: Path, path_map: dict[str, str], log) -> bool:
    if not path_map:
        return True

    from bag.workshop_imports import (
        apply_import_repairs,
        verify_repo_integrity,
    )

    # Note: path_map keys are relative to workshop_bench
    # apply_import_repairs needs them relative to sam_root for rewriting
    sam_path_map = {f"{WORKSHOP_ROOT}/{k}": f"{WORKSHOP_ROOT}/{v}" for k, v in path_map.items()}

    apply_import_repairs(sam_root, workshop, sam_path_map, log)

    if verify_repo_integrity(sam_root, workshop, log):
        from bag.bag_paths import apply_move_map
        apply_move_map(bag, sam_path_map, log)
        return True

    log.error("Workshop moves broke repo integrity â€” rolling back.")
    # Simple rollback for now
    for old_rel, new_rel in path_map.items():
        src = workshop / new_rel
        dst = workshop / old_rel
        if src.is_file():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
    return False


def apply_workshop_deletes(workshop: Path, paths: list, log, reason: str = "") -> list[str]:
    deleted = []
    suffix = f" ({reason})" if reason else ""
    for raw in paths or []:
        rel = raw.replace("\\", "/").strip("/")
        if not rel:
            continue
        target = workshop / rel
        if not target.exists():
            continue
        if not is_movable_bag_file(target, workshop):
            continue
        target.unlink()
        log.info(f"Workshop delete: {WORKSHOP_ROOT}/{rel}{suffix}")
        deleted.append(rel)
    return deleted


def organize_for_cycle(
    workshop: Path, idea: str, cycle: int, ask_gemini, log, root: Path | None = None
) -> str:
    # Resolve bag path (assumed to be near sam.py)
    sam_root = root or workshop.parent
    bag = sam_root / "bag"

    reg = load_registry(bag)
    file_listing = list_managed_files_for_prompt(workshop)

    prompt = (
        f"You are Sam tidying your workshop bench. Subfolders help organize your craft.\n\n"
        f"Cycle: {cycle}\n"
        f"Today's idea summary: {idea[:200]}\n\n"
        f"Existing files in {WORKSHOP_ROOT}/:\n"
        f"{file_listing}\n\n"
        f"Respond ONLY with JSON:\n"
        f'  - "target_folder": name of subfolder for NEW .py modules (e.g. "experiments")\n'
        f'  - "moves": list of {{"from": "path", "to": "folder/file.py"}} to tidy existing craft.\n'
        f'  - "deletes": list of paths to remove (obsolete only).\n'
    )

    raw = ask_gemini(prompt)
    try:
        data = json.loads(raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip())
    except Exception as e:
        data = {}

    target = sanitize_folder_name(data.get("target_folder", "") or reg.get("last_target", "my toys"))
    ensure_folder(workshop, bag, target, cycle=cycle)
    reg["last_target"] = target

    moves = data.get("moves", [])
    if not moves and file_listing != "  (none yet)":
        moves = infer_default_moves(workshop, target)

    moved, path_map = apply_workshop_moves(workshop, moves, log)
    if moved:
        finalize_workshop_moves(sam_root, workshop, bag, path_map, log)

    apply_workshop_deletes(workshop, data.get("deletes"), log, reason="workshop cleanup")

    save_registry(bag, reg)
    return target

