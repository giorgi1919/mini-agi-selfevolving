import ast
import yaml

# Loads forbidden rules from config.yml
with open("config.yml", "r") as f:
    CONFIG = yaml.safe_load(f)

FORBIDDEN = set(CONFIG["forbidden_imports"])

def is_safe(code: str) -> bool:
    """
    Checks Python AST for forbidden imports.
    """
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

    return True
