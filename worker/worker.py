from plugins.example_plugin import process

def run_worker():
    print("Worker test:", process(5))

if __name__ == "__main__":
    run_worker()
