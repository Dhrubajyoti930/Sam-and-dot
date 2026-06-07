"""
Problem: Fragile string-based patching.
Solution: AST-based verification before modification.
Cleanup: Remove once stable integration with sam.py is verified.
"""
import ast

from difflib import SequenceMatcher

def fuzzy_verify(file_content: str, snippet: str, threshold: float = 0.8) -> bool:
    return SequenceMatcher(None, file_content, snippet).ratio() > threshold

def verify_patch(file_path: str, target_func: str) -> bool:
    with open(file_path, 'r') as f:
        tree = ast.parse(f.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == target_func:
            return True
    return False