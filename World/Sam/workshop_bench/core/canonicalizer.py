import re

def canonicalize(text: str) -> str:
    """Strip boilerplate and normalize whitespace for semantic hashing."""
    text = re.sub(r'\s+', ' ', text)
    return text.strip().lower()