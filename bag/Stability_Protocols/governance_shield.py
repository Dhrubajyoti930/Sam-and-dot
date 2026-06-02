import re
def check_semantic_safety(plan):
    forbidden = [
        r"Path\.unlink", r"os\.unlink", r"os\.rmdir", 
        r"subprocess", r"shell=True", r"wisdom\.txt", 
        r"motion\.md", r"SAM_PERSONALITY\.md", r"dot\.py"
    ]
    return not any(re.search(pat, plan) for pat in forbidden)