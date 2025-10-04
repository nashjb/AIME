from obsidian_parser.note import Note
from typing import List
import task_utils  # your existing helper module

def get_today_note(vault_path:str, journal_root:str)->Note|None:
    return task_utils.get_note_for_today(vault_path, journal_root)

def build_shocker_tasks(note: Note):
    note_tasks = note.tasks
    dv_fields  = note.dataview_fields
    from models import ShockerTask
    sts = [ShockerTask(task=t) for t in note_tasks]
    for f in dv_fields:
        if f.key == "[clock":
            for i,t in enumerate(note_tasks):
                if t.line_number == f.line_number - 1:
                    sts[i].clocks.append(f); break
    return sts
