"""
modules/__init__.py
Tag registry for all Sam modules and scripts.
Each entry: { "name": str, "tagline": str, "type": "module"|"script" }
"""

import os
import json

TAG_REGISTRY_PATH = os.path.join(os.path.dirname(__file__), "..", "tag_registry.json")


def load_registry() -> list:
    """Load the tag registry from disk."""
    if not os.path.exists(TAG_REGISTRY_PATH):
        return []
    with open(TAG_REGISTRY_PATH, "r") as f:
        return json.load(f)


def get_module_taglines() -> list:
    """Return tagline strings for all modules."""
    return [f"{e['name']}: {e['tagline']}" for e in load_registry() if e["type"] == "module"]


def get_script_taglines() -> list:
    """Return tagline strings for all scripts."""
    return [f"{e['name']}: {e['tagline']}" for e in load_registry() if e["type"] == "script"]


def register_entry(name: str, tagline: str, entry_type: str) -> bool:
    """Add a new module or script to the tag registry."""
    registry = load_registry()
    for entry in registry:
        if entry["name"] == name:
            entry["tagline"] = tagline
            break
    else:
        registry.append({"name": name, "tagline": tagline, "type": entry_type})
    with open(TAG_REGISTRY_PATH, "w") as f:
        json.dump(registry, f, indent=2)
    return True
