import time
from datetime import datetime
from obsidian_parser import Note, Vault
from pathlib import Path
from datetime import date
from shocker_task import ShockerTask


def get_note_for_today(vault_path: str, journal_root: str) -> Note | None:
    vault = Vault(Path(vault_path))

    today = date.today()
    note_path = f"{journal_root}/{today.year}/{today.strftime('%m')}/{today.isoformat()}.md"
    note = vault.get_note(note_path)

    if note is None:
        print(f"Note not found: {note_path}")
        return None

    return note



def load_tasks_linked_to_note(note: Note) -> list[ShockerTask]:
    my_tasks: list[ShockerTask] = []
    lines = note.path.read_text(encoding="utf-8").splitlines()

    offset = 0
    #if lines and lines[0].strip() == "---":
     #   for i in range(1, len(lines)):
      ##      if lines[i].strip() == "---":
        #        offset = i + 1  # first line after closing ---
    

    for task in note.tasks:
        my_tasks.append(ShockerTask.from_task(task, note, offset))

    return my_tasks
