import os
import subprocess
import sys
from pathlib import Path

# Resource caps: 4 cores, 4GB RAM, 20s wall time
MAX_CORES = 4
MAX_RAM_BYTES = 4 * 1024 * 1024 * 1024
TEST_TIMEOUT = 20
PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)


def _limit_resources():
    """
    Best-effort resource limiter for the pytest subprocess.
    """
    try:
        os.sched_setaffinity(0, set(range(MAX_CORES)))
    except AttributeError:
        # sched_setaffinity not available on this platform
        pass
    except PermissionError:
        pass

    try:
        import resource

        resource.setrlimit(resource.RLIMIT_AS, (MAX_RAM_BYTES, MAX_RAM_BYTES))
        # CPU time cap to avoid runaway tests (wall timeout also applied)
        resource.setrlimit(resource.RLIMIT_CPU, (TEST_TIMEOUT, TEST_TIMEOUT + 5))
    except Exception:
        # If resource module or limits fail, continue without crashing
        pass


def run_tests() -> bool:
    """
    Runs pytest under resource limits and returns True if all tests passed.
    """
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-q"],
            capture_output=True,
            text=True,
            timeout=TEST_TIMEOUT,
            preexec_fn=_limit_resources if os.name == "posix" else None,
            env={
                **os.environ,
                "PYTHONWARNINGS": "ignore",
                "PYTHONPATH": PROJECT_ROOT,
            }
        )
    except subprocess.TimeoutExpired:
        print("[TESTER] ❌ Tests timed out")
        return False
    except Exception as exc:
        print(f"[TESTER] ❌ Test execution failed: {exc}")
        return False

    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(result.stderr.strip())

    return result.returncode == 0
