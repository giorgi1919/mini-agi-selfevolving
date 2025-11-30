import subprocess

def run_tests() -> bool:
    """
    Runs pytest and returns True if all tests passed.
    """
    result = subprocess.run(
        ["pytest", "-q"],
        capture_output=True,
        text=True
    )
    return result.returncode == 0
