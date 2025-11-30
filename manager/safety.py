import ast
import yaml
from pathlib import Path

# Loads forbidden rules from config.yml
with open("config.yml", "r") as f:
    CONFIG = yaml.safe_load(f)

FORBIDDEN = set(CONFIG["forbidden_imports"])
SAFE_DIRECTORIES = {Path(d).as_posix() for d in CONFIG.get("safe_directories", [])}
MAX_PATCH_LINES = int(CONFIG.get("max_patch_lines", 0))


def _in_safe_directory(path: Path) -> bool:
    return any(str(path).startswith(sd) for sd in SAFE_DIRECTORIES)


def _line_budget_ok(code: str) -> bool:
    if MAX_PATCH_LINES <= 0:
        return True
    return len(code.splitlines()) <= MAX_PATCH_LINES


def is_safe(code: str, target_path: str) -> bool:
    """
    Checks Python AST for forbidden imports and simple policy limits.
    """
    path = Path(target_path)

    if SAFE_DIRECTORIES and not _in_safe_directory(path):
        return False

    if not _line_budget_ok(code):
        return False

    try:
        tree = ast.parse(code)
    except Exception:
        return False

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                if name.name.split(".")[0] in FORBIDDEN:
                    return False

        if isinstance(node, ast.ImportFrom):
            if node.module and node.module.split(".")[0] in FORBIDDEN:
                return False

        if isinstance(node, ast.Call):
            # Block indirections like __import__, eval/exec that could bypass AST checks
            fn = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
            if fn in {"__import__", "eval", "exec"}:
                return False

    return True
