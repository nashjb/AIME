# server.py

import json
from datetime import datetime, timedelta
import os

def task_filename_for_today():
    date_str = datetime.today().strftime("%Y-%m-%d")
    return f"task-{date_str}.json"


def load_tasks_for_today():
    filename = task_filename_for_today()
    if not os.path.exists(filename):
        return []
    with open(filename, "r") as f:
        return json.load(f)

def save_tasks_for_today(tasks):
    filename = task_filename_for_today()
    with open(filename, "w") as f:
        json.dump(tasks, f, indent=2)

def parse_time_str(hhmm):
    return datetime.strptime(hhmm, "%H:%M").time()

def parse_duration_str(hhmm):
    h, m = map(int, hhmm.split(":"))
    return timedelta(hours=h, minutes=m)
