import random
from manager.safety import is_safe
from manager.tester import run_tests
from manager.evaluator import evaluate
from manager.applier import apply_patch
from manager.provenance import save_version
from manager.rollback import rollback

TARGET_FILE = "plugins/example_plugin.py"

def mutate_code(old: str) -> str:
    """
    Very primitive mutation: randomly rewrite comments or variable names.
    """
    lines = old.split("\n")
    new_lines = []

    for ln in lines:
        # 10% chance to mutate a line
        if random.random() < 0.10:
            new_lines.append(ln.replace("x", "val"))
        else:
            new_lines.append(ln)

    return "\n".join(new_lines)


def main():
    print("[MANAGER] Started")

    with open(TARGET_FILE, "r") as f:
        old_code = f.read()

    new_code = mutate_code(old_code)

    print("[MANAGER] Safety check...")
    if not is_safe(new_code):
        print("[MANAGER] ❌ Unsafe code detected")
        rollback(TARGET_FILE)
        return

    print("[MANAGER] Evaluation...")
    if not evaluate(old_code, new_code):
        print("[MANAGER] ❌ Evaluation failed")
        rollback(TARGET_FILE)
        return

    print("[MANAGER] Applying update...")
    save_version(TARGET_FILE, old_code)
    apply_patch(TARGET_FILE, new_code)

    print("[MANAGER] Running tests...")
    if not run_tests():
        print("[MANAGER] ❌ Tests failed — rolling back")
        rollback(TARGET_FILE)
    else:
        print("[MANAGER] ✅ Update accepted")

if __name__ == "__main__":
    main()
