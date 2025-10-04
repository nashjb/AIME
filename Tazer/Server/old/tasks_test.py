# test.py

import time
import server
import task_utils
import asyncio
import re
from tazer import TazerClient
from datetime import datetime
import subprocess
from typing import List
from obsidian_parser.models.dataview import DataviewInlineField
from obsidian_parser.note import WikiLink

from datetime import datetime

from pathlib import Path
import os

vault_path = "C:/Users/nash/OneDrive/Documents/Vault"
vault_name = "Vault"
journal_root = "Journal/01 Daily"

vibrate_time = "7:00"
wakeup_time = "8:00"
vibrate_done = False
shock_done   = False

DEVICE_ADDRESS = "c2:dd:fc:87:e1:81"
CHARACTERISTIC_UUID = "beb5483e-36e1-4688-b7f5-ea07361b26a8"

class ShockerTask:
    def __init__(self, task: WikiLink, clocks: list[DataviewInlineField] | None = None):
        self.task = task
        self.clocks = clocks or []
        self.start_time = None
        self.end_time = None

        # Try to extract "HH:MM - HH:MM" at the beginning of the task text
        time_match = re.match(r"^(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})", task.text)
        if time_match:
            self.start_time, self.end_time = time_match.groups()

    def add_clock(self, clock: DataviewInlineField):
        """Add a DataviewInlineField clock entry."""
        self.clocks.append(clock)


    def mark_status(self, status: str) -> None:
        if status not in {"vibrated", "shocked"}:
            print(f"[ERROR] Invalid status '{status}'. Use 'vibrated' or 'shocked'.")
            return
        if self.line_number is None or not self.note:
            print("[ERROR] Cannot mark status: missing line_number or note")
            return
        try:
            lines = self.note.path.read_text(encoding="utf-8").splitlines()
            if self.line_number >= len(lines):
                print(f"[ERROR] Line number {self.line_number} out of range")
                return

            line = lines[self.line_number]
            if self.text.strip() not in line:
                print(f"[WARN] Task text '{self.text}' not found in expected line")

            # Replace existing [status:: ...] or append a new one
            pattern = r"\[status::\s*([^\]]+)\]"
            if re.search(pattern, line):
                new_line = re.sub(pattern, f"[status:: {status}]", line)
            else:
                new_line = line.rstrip() + f" [status:: {status}]"

            if new_line == line:
                print(f"[INFO] Status already '{status}'")
                return

            lines[self.line_number] = new_line
            updated = "\n".join(lines)
            self.note.path.write_text(updated, encoding="utf-8")
            self.note._raw_content = updated
            print(f"[SUCCESS] Marked task '{self.text}' as status '{status}'")
        except Exception as e:
            print(f"[ERROR] Failed to mark status: {e}")

    def mark_vibrated(self) -> None:
        self.mark_status("vibrated")

    def mark_shocked(self) -> None:
        self.mark_status("shocked")



    def __repr__(self):
        return (
            f"ShockerTask(task={self.task!r}, "
            f"clocks={self.clocks!r}, "
            f"start_time={self.start_time!r}, "
            f"end_time={self.end_time!r})"
        )


# First thing here is to create the note if it doesn't exist using the cli







while (True):

    # If daily note doesn't exist
    note = task_utils.get_note_for_today(vault_path, journal_root)

    # This part I want vibrate_time = "7:00"
# wakeup_time = "8:00" just use print so then I know so if the note doesn't exist 
    now = datetime.now().strftime("%H:%M")

  

    if not note:
    # Vibrate check (only once after vibrate_time)
        if not vibrate_done and now >= vibrate_time:
            print("vibrate")
            vibrate_done = True

        # Shock check (only once after wakeup_time)
        if not shock_done and now >= wakeup_time:
            print("shock")
            shock_done = True
        # os.startfile("obsidian://adv-uri?vault=Vault&daily=true&mode=append")

    else:
        # we get the tasks 
        note_tasks = note.tasks
        note_frontmatter = note.dataview_fields


        # Create a ShockerTask object for every task so the lengths always match
        shocker_task_list = [ShockerTask(task=current_task, clocks=[]) for current_task in note_tasks]

        # Go through each frontmatter entry and check if it is a clock
        for frontmatter_entry in note_frontmatter:
            if frontmatter_entry.key == "[clock":
                # Look for the task that sits one line above this clock
                for task_index, current_task in enumerate(note_tasks):
                    if current_task.line_number == frontmatter_entry.line_number - 1:
                        # Attach the clock to the correct ShockerTask
                        shocker_task_list[task_index].clocks.append(frontmatter_entry)
                        break  # move on once we found the matching task




        def parse_hhmm_to_time(hhmm_str: str):
            return datetime.strptime(hhmm_str, "%H:%M").time()

        # If you already have currentTime as a "HH:MM" string, use this:
        # current_time = parse_hhmm_to_time(currentTime)
        # Otherwise, use the current system time:
        current_time = datetime.now().time()

        for shocker_task in shocker_task_list:

            # Skip tasks without parsed start_time
            
            if not shocker_task.start_time:
                continue

            try:
                task_start_time = parse_hhmm_to_time(shocker_task.start_time)
            except ValueError:
                # Bad time format; skip safely
                continue

            clocks_are_empty = len(shocker_task.clocks) == 0
            task_is_incomplete = (shocker_task.task.status == ' ')

            # Trigger if we've hit or passed the start time,
            # the task is still incomplete, and no clocks are recorded.
            if task_start_time <= current_time and task_is_incomplete and clocks_are_empty:
                print("SHOCKING FOR TASK:   " + shocker_task.task.text)