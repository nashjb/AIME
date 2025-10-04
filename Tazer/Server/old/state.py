import json, os
from config import STATE_FILE
from time_utils import today_id

def load():
    if os.path.exists(STATE_FILE): return json.load(open(STATE_FILE, "r"))
    return {}
def save(s): json.dump(s, open(STATE_FILE, "w"), indent=2)
def get_flags(s): return s.setdefault(today_id(), {"vibrate_done": False, "shock_done": False})
