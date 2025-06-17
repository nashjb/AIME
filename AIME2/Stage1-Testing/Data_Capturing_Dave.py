# Data_Capturing_Dave.py
from pylsl import StreamInlet, resolve_stream
import numpy as np
import os
import time
FFT_MAX_HZ = 60


def collect_data(action):
    print("Starting data collection. Press Enter to stop...")

    # Resolve an EEG stream and create an inlet
    streams = resolve_stream('type', 'EEG')
    inlet = StreamInlet(streams[0])

    channel_datas = []
    start_time = time.time()
    print("Collecting data...")
    while True:
        sample, timestamp = inlet.pull_sample()
        if sample:
            # Truncate or pad the sample to ensure it has a consistent size
            channel_data = sample[:FFT_MAX_HZ] if len(sample) >= FFT_MAX_HZ else sample + [0]*(FFT_MAX_HZ-len(sample))
            channel_datas.append(channel_data)

            # Log data collection progress
            if len(channel_datas) % 100 == 0:  # Log every 100 samples
                print(f"Collected {len(channel_datas)} samples...")

        # Check for the Enter key press to stop collection
        if input("Press Enter to stop...") == '':
            break

    print(f"Data collection stopped. Total time: {time.time() - start_time} seconds")
    return channel_datas

def save_data(action, channel_datas):
    datadir = "data"
    os.makedirs(datadir, exist_ok=True)
    actiondir = os.path.join(datadir, action)
    os.makedirs(actiondir, exist_ok=True)

    filepath = os.path.join(actiondir, f"{int(time.time())}.npy")
    np.save(filepath, np.array(channel_datas))
    print(f"Data saved under {filepath}")

def main():
    print("Press Enter to start...")
    input()
    action = input("Enter the action name to save this data as: ")
    channel_datas = collect_data(action)
    save_data(action, channel_datas)

if __name__ == "__main__":
    main()
