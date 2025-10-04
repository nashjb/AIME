import time
import os
from datetime import datetime
import notifier
import config
from obsidian_parser import WikiLink
from shocker_task import ShockerTask
import task_utils

def main():
    
    note = task_utils.get_note_for_today(config.VAULT_PATH, config.JOURNAL_ROOT)
    day_tasks: list[ShockerTask] = []

    def rebuild():
        note = task_utils.get_note_for_today(config.VAULT_PATH, config.JOURNAL_ROOT)
        day_tasks = task_utils.load_tasks_linked_to_note(note) # This should return shocker tasks and include any fields available and clocks and shit


    while(True):

        if not note:
            vault_name = config.VAULT_NAME
            uri = f"obsidian://adv-uri?vault={vault_name}&daily=true&mode=append"
            os.startfile(uri)  # launches Obsidian with the URI
            print("Created daily note")
            time.sleep(10)  # check twice a minute
            note = task_utils.get_note_for_today(config.VAULT_PATH, config.JOURNAL_ROOT)

        currentTime = datetime.now()
        day_tasks = task_utils.load_tasks_linked_to_note(note) # This should return shocker tasks and include any fields available and clocks and shit


        # fuck what do I do here I need to be able to do something
        # ok I just need to focus on a callable method
        for day_task in day_tasks:
            print(day_task.raw_text)

            if day_task.startTime is not None:
                if day_task.startTime < currentTime:
                    if not day_task.isVibrated:
                        print("Vibrating Now")
                        day_task.setVibrate(True, rebuild)
                    else:
                        print("Already Vibrated")
                else:
                    print("Not Vibrated")
            else:
                print("No Time")

        time.sleep(10)  # check twice a minute





if __name__ == "__main__":
    main()
