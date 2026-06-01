def check_semantic_safety(plan):
    dangerous = ["os.remove", "rmdir", "shutil.rmtree"]
    return not any(cmd in plan for cmd in dangerous)