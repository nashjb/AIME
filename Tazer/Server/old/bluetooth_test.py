import time
import server
import task_utils
import asyncio
from tazer import TazerClient
from datetime import datetime

vault_path = "C:/Users/nash/OneDrive/Documents/Vault"
journal_root = "Journal/01 Daily"

DEVICE_ADDRESS = "58:8c:81:9e:8e:ca"
CHARACTERISTIC_UUID = "beb5483e-36e1-4688-b7f5-ea07361b26a8"

async def main_loop():
    tazer_client = TazerClient(DEVICE_ADDRESS, CHARACTERISTIC_UUID)

    while True:
        try:
            if not tazer_client.client.is_connected:
                while not tazer_client.client.is_connected:
                    print("[BLE] Reconnecting...")
                    try:
                        await tazer_client.connect()
                    except Exception as e:
                        print(f"[BLE] Reconnect failed: {e}")
                        await asyncio.sleep(2)  # wait before retrying
            
            number = int(input("Please write a number between 1–5 you want to send: "))
            if 1 <= number <= 5:
                await tazer_client.taze(number)  # or day_task.custom_fields.get("level", 3)

            else:
                print("❌ Invalid choice. Must be between 1 and 5.")
        except ValueError:
            print("❌ Please enter numbers only, not letters or symbols.")


asyncio.run(main_loop())
