import json
from pathlib import Path

def get_few_shot_example(task_category: str) -> str:
    exp_path = Path(__file__).parent / "experiences.json"
    if not exp_path.exists():
        return ""
    
    with open(exp_path) as f:
        data = json.load(f)
    
    candidates = [
        e for e in data 
        if e.get("sentiment") == "positive" and e.get("category") == task_category
    ]
    
    if candidates:
        best = candidates[-1]
        return f"Structure Example:\nSummary: {best['summary']}\nLearnings: {', '.join(best['key_learnings'])}"
    return ""