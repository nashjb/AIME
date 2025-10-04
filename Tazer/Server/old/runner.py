import time
from config import VAULT_PATH, JOURNAL_ROOT, VIBRATE_TIME, WAKEUP_TIME
from time_utils import passed, now_time
from state import load, save, get_flags
from obsidian_utils import get_today_note, build_shocker_tasks
from time_utils import parse_hhmm

def run():
    state = load()
    flags = get_flags(state)

    while True:
        note = get_today_note(VAULT_PATH, JOURNAL_ROOT)
        if not note:
            if not flags["vibrate_done"] and passed(VIBRATE_TIME): 
                from notifier import vibrate; vibrate(); flags["vibrate_done"]=True; save(state)
            if not flags["shock_done"] and passed(WAKEUP_TIME):    
                from notifier import shock; shock(); flags["shock_done"]=True; save(state)
        else:
            sts = build_shocker_tasks(note)
            ct = now_time()
            for st in sts:
                if not st.start_time: continue
                try:
                    if parse_hhmm(st.start_time) <= ct and getattr(st.task, "status", " ")==' ' and len(st.clocks)==0 and not st.shock_fired:
                        print("SHOCKING FOR TASK:", getattr(st.task, "text","")); st.shock_fired=True
                        # st.mark_status("shocked")  # enable if you want to persist
                except: pass

        time.sleep(30)
