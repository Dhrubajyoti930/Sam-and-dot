import json
from pathlib import Path

def log_critique(idea_json: dict, critique: str):
    log_path = Path(__file__).parent / "critique.log"
    with open(log_path, "a") as f:
        f.write(f"--- IDEA CRITIQUE ---\nIdea: {json.dumps(idea_json)}\nCritique: {critique}\n\n")