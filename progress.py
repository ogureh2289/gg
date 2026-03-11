import json
import os

PROGRESS_FILE = os.path.join(os.path.dirname(__file__), '..', 'progress.json')

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {"topic_index": 0, "task_num": 1, "tasks_done": 0}

def save_progress(data: dict):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(data, f)