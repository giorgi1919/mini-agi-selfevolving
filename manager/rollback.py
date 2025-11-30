import glob
import os
from pathlib import Path


def rollback(path: str):
    """
    Restores the latest backup for the target file if available.
    """
    target = Path(path)
    backup_dir = target.parent / "backups"
    pattern = str(backup_dir / f"{target.name}.backup_*")
    backups = sorted(glob.glob(pattern))

    if not backups:
        print("[ROLLBACK] No backup found. Manual restore recommended.")
        return False

    latest = backups[-1]
    with open(latest, "r") as f:
        code = f.read()

    with open(target, "w") as f:
        f.write(code)

    print(f"[ROLLBACK] Restored {target} from {latest}")
    return True
