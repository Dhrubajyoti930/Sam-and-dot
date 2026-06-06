"""
Problem: Fragile string-based patching.
Solution: AST-based verification before modification.
Cleanup: Remove once stable integration with sam.py is verified.
"""
import ast

def verify_patch(file_path: str, target_func: str) -> bool:
    with open(file_path, 'r') as f:
        tree = ast.parse(f.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == target_func:
            return True
    return False