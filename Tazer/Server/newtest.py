import os
import task_utils
import config
from shocker_task import ShockerTask


    
note = task_utils.get_note_for_today(config.VAULT_PATH, config.JOURNAL_ROOT)

day_tasks = task_utils.load_tasks_linked_to_note(note) # This should return shocker tasks and include any fields available and clocks and shit

for task in day_tasks:
    print("test")
    print(task.line_number)

