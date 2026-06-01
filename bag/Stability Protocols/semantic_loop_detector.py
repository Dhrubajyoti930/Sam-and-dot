
    for past in past_plans:
        # Simple overlap ratio as a proxy for similarity
        shared = set(new_plan.split()) & set(past.split())
        if len(shared) / max(len(new_plan.split()), 1) > threshold:
            return True
    return False