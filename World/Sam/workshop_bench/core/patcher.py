import ast

def apply_ast_patch(file_path: str, target_func: str, new_code: str):
    """Uses AST to locate function and replace body."""
    with open(file_path, 'r') as f:
        ast.parse(f.read())
    pass