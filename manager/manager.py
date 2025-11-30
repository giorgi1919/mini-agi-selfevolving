import importlib
import random
import textwrap
from pathlib import Path
from typing import List

from manager.applier import apply_patch
from manager.evaluator import evaluate
from manager.provenance import save_version
from manager.rollback import rollback
from manager.safety import is_safe
from manager.tester import run_tests

TARGET_FILE = Path("plugins/example_plugin.py")
CANDIDATES_PER_ROUND = 3


def mutate_code(old: str, seed: int) -> str:
    """
    Behaviour-preserving mutations with small refactors and comments to
    encourage gradual evolution rather than random corruption.
    """
    random.seed(seed)
    lines = old.splitlines()
    new_lines: List[str] = []
    renamed_arg = random.random() < 0.5
    arg_name = "value" if renamed_arg else "x"

    for ln in lines:
        stripped = ln.strip()
        if stripped.startswith("def process("):
            new_lines.append(f"def process({arg_name}):")
            if random.random() < 0.7:
                new_lines.append(
                    '    """Auto-evolved step: keep output stable while improving readability."""'
                )
            continue

        if stripped.startswith("return ") and "x" in stripped:
            # Keep semantics stable: still return +1
            new_lines.append(f"    result = {arg_name} + 1")
            new_lines.append("    return result")
            continue

        if renamed_arg and "x" in ln and "return" not in ln:
            new_lines.append(ln.replace("x", arg_name))
        else:
            new_lines.append(ln)

    if random.random() < 0.3:
        new_lines.append("")
        new_lines.append("# Evolution note: validated to preserve process behavior.")

    return "\n".join(new_lines)


def generate_candidates(old_code: str) -> List[str]:
    seeds = [random.randint(1, 10_000) for _ in range(CANDIDATES_PER_ROUND)]
    return [mutate_code(old_code, seed) for seed in seeds]


def preview_diff(old: str, new: str) -> str:
    return textwrap.shorten(new.replace("\n", " "), width=120, placeholder=" ...")


def answer_terminal_question():
    """
    Optional lightweight interaction loop to satisfy "answer in terminal".
    """
    try:
        question = input("[CHAT] Ask a question (empty to skip): ").strip()
    except EOFError:
        return

    if not question:
        return

    print(f"[CHAT] You asked: {question}")
    try:
        # Reload to use the latest plugin code
        plugin = importlib.import_module("plugins.example_plugin")
        importlib.reload(plugin)
        sample = plugin.process(5)
        print(f"[CHAT] Current process(5) -> {sample}")
    except Exception as exc:
        print(f"[CHAT] Unable to run plugin: {exc}")


def process_candidate(old_code: str, candidate: str, backup_path) -> str:
    """
    Apply, test, and either accept or rollback a candidate.
    Returns the accepted code (old or new).
    """
    print(f"[MANAGER] Candidate preview: {preview_diff(old_code, candidate)}")

    print("[MANAGER] Safety check...")
    if not is_safe(candidate, str(TARGET_FILE)):
        print("[MANAGER] ❌ Unsafe code detected")
        rollback(str(TARGET_FILE))
        return old_code

    print("[MANAGER] Evaluation...")
    if not evaluate(old_code, candidate):
        print("[MANAGER] ❌ Evaluation failed")
        rollback(str(TARGET_FILE))
        return old_code

    print("[MANAGER] Applying update...")
    apply_patch(str(TARGET_FILE), candidate)

    print("[MANAGER] Running tests...")
    if not run_tests():
        print("[MANAGER] ❌ Tests failed — rolling back")
        rollback(str(TARGET_FILE))
        return old_code

    print("[MANAGER] ✅ Update accepted")
    return candidate


def main(rounds: int = 1):
    print("[MANAGER] Started")

    old_code = TARGET_FILE.read_text()
    backup_path = save_version(str(TARGET_FILE), old_code)
    print(f"[MANAGER] Backup saved to {backup_path}")

    for round_idx in range(rounds):
        print(f"[MANAGER] ---- Evolution round {round_idx + 1} ----")
        candidates = generate_candidates(old_code)
        for candidate in candidates:
            updated = process_candidate(old_code, candidate, backup_path)
            if updated != old_code:
                old_code = updated

    answer_terminal_question()


if __name__ == "__main__":
    main(rounds=2)
