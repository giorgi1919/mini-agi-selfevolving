import time
from pathlib import Path


def save_version(path: str, code: str):
    """
    Writes a timestamped backup alongside the target file.
    """
    target = Path(path)
    backup_dir = target.parent / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)

    timestamp = int(time.time())
    backup_path = backup_dir / f"{target.name}.backup_{timestamp}"

    with open(backup_path, "w") as f:
        f.write(code)

    return backup_path
