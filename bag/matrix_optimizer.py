import json

def get_matrix():
    """Generates a Minimum Viable Test Matrix."""
    # Default stable baseline
    matrix = {"include": [{"os": "ubuntu-latest", "python": "3.12"}]}
    try:
        # Simple heuristic: scan for newer features in sam.py
        with open("sam.py", "r") as f:
            content = f.read()
            # If we use advanced async or type hinting, ensure 3.11+
            if "asyncio" in content:
                matrix["include"].append({"os": "ubuntu-latest", "python": "3.13"})
    except Exception:
        pass
    return matrix

if __name__ == "__main__":
    print(json.dumps(get_matrix()))