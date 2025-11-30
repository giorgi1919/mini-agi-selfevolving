import os
import tempfile
from pathlib import Path


def apply_patch(path: str, new_code: str):
    """
    Atomically writes new code to the target path.
    """
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile("w", delete=False, dir=target.parent) as tmp:
        tmp.write(new_code)
        tmp_path = Path(tmp.name)

    os.replace(tmp_path, target)
