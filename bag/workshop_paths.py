"""Shared path rules for bag/ workshop files (root and subfolders)."""

from pathlib import Path

BLOCKED_DIR_NAMES = frozenset({"rollback_registry", "__pycache__", ".git"})

# Root-level bag/*.py that Sam must never patch or delete via workshop flows
ROOT_PROTECTED_PY = frozenset({
    "dot.py", "emailer.py", "evaluator.py", "matrix_optimizer.py",
    "semantic_cache.py", "tests.py", "versioning.py", "worklog.py", "prompts.py",
    "patch_ops.py", "workshop.py", "workshop_paths.py", "workshop_imports.py",
    "critique.py",
})

FORBIDDEN_BASENAMES = frozenset({
    "wisdom.txt", "motion.md", "SAM_PERSONALITY.md", "dot.py",
})


def relative_bag_posix(path: Path, bag: Path) -> str:
    return path.relative_to(bag).as_posix()


def normalize_bag_rel(rel: str) -> str:
    """Path relative to bag/ (no leading bag/)."""
    rel = str(rel or "").replace("\\", "/").strip().lstrip("/")
    if rel.startswith("bag/"):
        rel = rel[4:]
    return rel


def is_blocked_relative(rel: str) -> bool:
    parts = Path(rel).parts
    return any(p in BLOCKED_DIR_NAMES for p in parts)


def is_allowed_workshop_destination(path: Path, bag: Path) -> bool:
    """Whether a .py path may be used as a move target (file may not exist yet)."""
    if path.suffix != ".py":
        return False
    try:
        rel = relative_bag_posix(path, bag)
    except ValueError:
        return False
    if is_blocked_relative(rel):
        return False
    if path.name in FORBIDDEN_BASENAMES:
        return False
    parts = Path(rel).parts
    if len(parts) == 1 and parts[0] in ROOT_PROTECTED_PY:
        return False
    return True


def is_writable_bag_py(path: Path, bag: Path) -> bool:
    if path.suffix != ".py":
        return False
    try:
        rel = relative_bag_posix(path, bag)
    except ValueError:
        return False
    if is_blocked_relative(rel):
        return False
    if path.name in FORBIDDEN_BASENAMES:
        return False
    parts = Path(rel).parts
    if len(parts) == 1 and parts[0] in ROOT_PROTECTED_PY:
        return False
    return True


def iter_writable_bag_py(bag: Path):
    for f in sorted(bag.rglob("*.py")):
        if is_writable_bag_py(f, bag):
            yield f


def is_allowed_patch_filename(fname: str) -> bool:
    if fname == "sam.py":
        return True
    if not fname.startswith("bag/"):
        return False
    rel = fname[4:]
    if ".." in rel.replace("\\", "/").split("/"):
        return False
    if not rel.endswith(".py"):
        return False
    if is_blocked_relative(rel):
        return False
    if Path(rel).name in FORBIDDEN_BASENAMES:
        return False
    parts = Path(rel).parts
    if len(parts) == 1 and parts[0] in ROOT_PROTECTED_PY:
        return False
    return True
