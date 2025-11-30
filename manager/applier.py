def apply_patch(path: str, new_code: str):
    with open(path, "w") as f:
        f.write(new_code)
