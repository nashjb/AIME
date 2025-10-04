import asyncio
from bleak import BleakClient

class TazerClient:
    def __init__(self, address: str, characteristic_uuid: str):
        self.address = address
        self.char_uuid = characteristic_uuid
        self.client = BleakClient(address)

    async def connect(self):
        print(f"[BLE] Connecting to {self.address}...")
        await self.client.connect()

        if self.client.is_connected:
            print("[BLE] ✅ Connected.")
        else:
            raise ConnectionError("[BLE] ❌ Failed to connect.")

    async def taze(self, level: int):
        if not 1 <= level <= 5:
            print("[ERROR] Level must be between 1 and 5.")
            return

        if not self.client.is_connected:
            print("[ERROR] Client is not connected.")
            return

        payload = str(level).encode()
        print(f"[TASER] Sending ASCII '{level}' → {payload}")
        await self.client.write_gatt_char(self.char_uuid, payload)
        print("[TASER] ⚡ ZAP sent!")

    async def disconnect(self):
        if self.client.is_connected:
            print("[BLE] Disconnecting...")
            await self.client.disconnect()
            print("[BLE] Disconnected.")
