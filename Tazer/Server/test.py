import os
import task_utils
import config
from shocker_task import ShockerTask


    
note = task_utils.get_note_for_today(config.VAULT_PATH, config.JOURNAL_ROOT)
day_tasks: list[ShockerTask] = []

def rebuild():
    note = task_utils.get_note_for_today(config.VAULT_PATH, config.JOURNAL_ROOT)
    day_tasks = task_utils.load_tasks_linked_to_note(note) # This should return shocker tasks and include any fields available and clocks and shit


if not note:
    vault_name = config.VAULT_NAME
    uri = f"obsidian://adv-uri?vault={vault_name}&daily=true&mode=append"
    os.startfile(uri)  # launches Obsidian with the URI
    print("Created daily note")
else:
    print("Note already exists")

my_tasks = note.tasks
shocker_tasks = []

for task in note.tasks:
    print("test")
    print(note.tasks[0].line_number)
    shocker_task = ShockerTask.from_task(task, note)
   # print("After process:    " +  str(shocker_task.line_number))
   # shocker_task.setVibrate(True, rebuild)


