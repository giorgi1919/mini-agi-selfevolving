def evaluate(old_code: str, new_code: str) -> bool:
    """
    Very simple evaluation:
    - New code must be different
    - Not empty
    - Not drastically shorter
    """
    if new_code.strip() == "":
        return False

    if new_code == old_code:
        return False

    if len(new_code) < len(old_code) * 0.5:
        return False

    return True
