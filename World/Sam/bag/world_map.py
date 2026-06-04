import json
from pathlib import Path

WORLD_MAP_PATH = Path(__file__).parent.parent.parent.parent / "World" / "map.json"

def update_map(root: Path):
    """Scan the World and generate a searchable index for Sam and Dot."""
    map_data = {
        "heart": "World/Sam/sam.py",
        "brain": "World/Sam/My_memories/",
        "watchdog": "World/Dot/dot.py",
        "post_office": "World/mail/",
        "modules": [],
        "tests": [],
        "last_updated": ""
    }

    # Scan for modules and tests
    for p in root.rglob("*.py"):
        rel = p.relative_to(root).as_posix()
        if "tests.py" in rel or "test_" in rel:
            map_data["tests"].append(rel)
        elif "sam.py" not in rel and "dot.py" not in rel:
            map_data["modules"].append(rel)

    with open(WORLD_MAP_PATH, "w") as f:
        json.dump(map_data, f, indent=2)
    return map_data

def get_map_summary():
    """Return a brief string summary of the World for inclusion in prompts."""
    if not WORLD_MAP_PATH.exists():
        return "World Map not yet initialized."
    try:
        data = json.loads(WORLD_MAP_PATH.read_text())
        return (f"World Map: {len(data['modules'])} modules, {len(data['tests'])} tests found. "
                f"Core logic is in {data['heart']}.")
    except:
        return "World Map corrupted."
