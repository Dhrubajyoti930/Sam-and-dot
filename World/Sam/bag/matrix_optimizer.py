import json
from pathlib import Path

# Fix #6 -- absolute path so this works regardless of working directory
SAM_PY = Path(__file__).parent.parent / "sam.py"


def get_matrix():
    """Generates a Minimum Viable Test Matrix."""
    # Default stable baseline
    matrix = {"include": [{"os": "ubuntu-latest", "python": "3.12"}]}
    try:
        with open(SAM_PY, "r") as f:
            content = f.read()
            if "asyncio" in content:
                matrix["include"].append({"os": "ubuntu-latest", "python": "3.13"})
    except Exception:
        pass
    return matrix


if __name__ == "__main__":
    print(json.dumps(get_matrix()))
