# main.py

import time
import server
import task_utils
import asyncio
from tazer import TazerClient
from datetime import datetime

vault_path = "C:/Users/nash/OneDrive/Documents/Vault"
journal_root = "Journal/01 Daily"

DEVICE_ADDRESS = "c2:dd:fc:87:e1:81"
CHARACTERISTIC_UUID = "beb5483e-36e1-4688-b7f5-ea07361b26a8"

async def main_loop():
    tazer_client = TazerClient(DEVICE_ADDRESS, CHARACTERISTIC_UUID)

    try:
        while True:
            if not tazer_client.client.is_connected:
                print("[BLE] Reconnecting...")
                await tazer_client.connect()
            note = task_utils.get_note_for_today(vault_path, journal_root)
            if note:
                day_tasks = task_utils.load_tasks_linked_to_note(vault_path, note)
                for day_task in day_tasks:
                    print(day_task)
                    if task_utils.should_shock(day_task):
                        print(f"[TASK] Overdue: {day_task.text}")
                        await tazer_client.taze(3)  # or day_task.custom_fields.get("level", 3)
                        day_task.mark_failed()
            await asyncio.sleep(60)
    finally:
        await tazer_client.disconnect()

if __name__ == "__main__":
    asyncio.run(main_loop())
