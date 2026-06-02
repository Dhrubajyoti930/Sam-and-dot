

def get_intent_category(task_description: str) -> str:
    return "Refactoring"

def get_context_slice(intent: str) -> str:
    return f"Context for {intent}"