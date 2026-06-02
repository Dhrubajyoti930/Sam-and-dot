"""Shared path rules for Sam's World structure."""

from pathlib import Path

# Areas Sam may use for workshop craft
WORKSHOP_ROOT = "workshop_bench"
PROMPT_ROOT = "Gemini_note_pad"
GOVERNANCE_ROOT = "bag"

BLOCKED_DIR_NAMES = frozenset({"rollback_registry", "__pycache__", ".git", "trash"})

# Files Sam must never patch or delete via workshop flows
INFRA_FILENAMES = frozenset({
    "dot.py", "emailer.py", "evaluator.py", "matrix_optimizer.py",
    "semantic_cache.py", "tests.py", "versioning.py", "worklog.py",
    "workshop.py", "workshop_paths.py", "workshop_imports.py",
    "patch_ops.py", "bag_paths.py", "critique.py",
    "wisdom.txt", "SAM_PERSONALITY.md", "WHO_I_AM.md", "goals.json",
    "experiences.json", "cycle_status.txt", "motion.md"
})

# Alias for backward compatibility
FORBIDDEN_BASENAMES = INFRA_FILENAMES

# Phase VI may patch only this registry file
PROMPT_REGISTRY_REL = f"{PROMPT_ROOT}/prompts.py"


def relative_posix(path: Path, base: Path) -> str:
    return path.relative_to(base).as_posix()


# Alias for backward compatibility during migration
relative_bag_posix = relative_posix


def is_movable_bag_file(path: Path, workshop: Path) -> bool:
    """Whether Sam may relocate or delete this file (any type under workshop_bench/)."""
    if not path.is_file():
        return False
    if path.name in INFRA_FILENAMES:
        return False
    # Must be under workshop_bench
    try:
        rel = path.relative_to(workshop)
    except ValueError:
        return False

    parts = rel.parts
    if any(p in BLOCKED_DIR_NAMES for p in parts):
        return False
    return True


def iter_movable_bag_files(workshop: Path):
    for f in sorted(workshop.rglob("*")):
        if is_movable_bag_file(f, workshop):
            yield f


def is_writable_bag_py(path: Path, workshop: Path) -> bool:
    if path.suffix != ".py":
        return False
    return is_movable_bag_file(path, workshop)


def iter_writable_bag_py(workshop: Path):
    for f in sorted(workshop.rglob("*.py")):
        if is_writable_bag_py(f, workshop):
            yield f


def is_allowed_patch_filename(fname: str) -> bool:
    """Check if Sam is allowed to apply a surgical patch to this filename (relative to Sam's root)."""
    p = Path(fname)
    if fname == "sam.py":
        return True
    if fname == PROMPT_REGISTRY_REL:
        return True

    # Allow patching anything in workshop_bench that isn't infra
    if fname.startswith(f"{WORKSHOP_ROOT}/"):
        if p.name in INFRA_FILENAMES:
            return False
        if any(part in BLOCKED_DIR_NAMES for part in p.parts):
            return False
        return p.suffix == ".py"

    return False
