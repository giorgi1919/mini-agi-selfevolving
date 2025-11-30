import time

def save_version(path: str, code: str):
    timestamp = int(time.time())
    with open(f"{path}.backup_{timestamp}", "w") as f:
        f.write(code)
