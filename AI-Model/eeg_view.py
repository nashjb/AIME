"""
eeg_view.py – stand-alone LSL EEG viewer with diagnostics.
Run:  python eeg_view.py
"""

# ── Force a GUI backend before importing pyplot ─────────────────────────────
import matplotlib
matplotlib.use("TkAgg")            # change to "QtAgg" for PyQt if you like

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from pylsl import StreamInlet, resolve_byprop
import numpy as np
from collections import deque
import time, sys

# ───────────────────────── helper ───────────────────────────────────────────
def wait_for_eeg(timeout_per_try=5, retry_pause=2):
    """Block until an EEG LSL stream appears, then return (inlet, info)."""
    attempt = 0
    while True:
        streams = resolve_byprop("type", "EEG", timeout=timeout_per_try)
        if streams:
            info = streams[0]
            print(f"[INFO] Connected to EEG stream: {info.name()} "
                  f"({info.channel_count()} ch, {info.nominal_srate()} Hz)")
            return StreamInlet(info), info
        attempt += 1
        print(f"[WARN] No EEG stream (attempt {attempt}), retrying…", file=sys.stderr)
        time.sleep(retry_pause)

# ───────────────────────── live viewer ──────────────────────────────────────
def start_live_viewer(window_s: float = 1.0):
    inlet, info = wait_for_eeg()
    n_chan = info.channel_count()
    srate  = info.nominal_srate() or 250
    buf_len = int(window_s * srate)

    buffers = [deque(maxlen=buf_len) for _ in range(n_chan)]
    times   = deque(maxlen=buf_len)
    start_t = None

    plt.style.use("seaborn-v0_8-darkgrid")
    fig, axes = plt.subplots(n_chan, 1, sharex=True,
                             figsize=(10, 2 * n_chan),
                             constrained_layout=True)
    lines = []
    for ch, ax in enumerate(axes):
        line, = ax.plot([], [], lw=1)
        ax.set_ylabel(f"Ch {ch+1}")
        ax.set_ylim(-100, 100)
        lines.append(line)
    axes[-1].set_xlabel("Time (s)")

    print("[INFO] Opening EEG live viewer window…")

    # ── animation callback ─────────────────────────────────────────────────
    def update(_):
        nonlocal start_t
        new_pts = 0
        for _ in range(10):                         # grab up to 10 samples
            sample, ts = inlet.pull_sample(timeout=0.1)
            if sample is None:
                break
            if start_t is None:
                start_t = ts
            t_rel = ts - start_t
            times.append(t_rel)
            for ch, val in enumerate(sample):
                buffers[ch].append(val)
            new_pts += 1

        if new_pts == 0:
            return lines

        t = np.asarray(times)
        right = t[-1]
        left  = right - window_s if right > window_s else 0

        for ch, (ax, line) in enumerate(zip(axes, lines)):
            line.set_data(t, np.asarray(buffers[ch]))
            ax.set_xlim(left, right)
            ax.relim(); ax.autoscale_view(scalex=False, scaley=True)
        return lines

    # Keep a reference so the animation isn't garbage-collected
    anim = FuncAnimation(fig, update, interval=40, blit=False)

    plt.show()

# ───────────────────────── CLI entry-point ──────────────────────────────────
if __name__ == "__main__":
    start_live_viewer()
