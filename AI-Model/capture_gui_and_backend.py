# capture_gui_and_backend.py
import tkinter as tk
from tkinter import ttk, messagebox
import threading, queue, time, os, sys, numpy as np
from pylsl import StreamInlet, resolve_byprop
from eeg_view import start_live_viewer

FFT_MAX_HZ = 60  # keep first 60 bins per sample

# ───────────────────────────────── capture thread ───────────────────────────
class CaptureThread(threading.Thread):
    def __init__(self, save_dir: str, q: queue.Queue):
        super().__init__(daemon=True)
        self.save_dir, self.q = save_dir, q
        self.stopflag = threading.Event()

    def run(self):
        try:
            streams = resolve_byprop("type", "EEG", timeout=5)
            inlet   = StreamInlet(streams[0])
        except Exception as e:
            self.q.put(("error", f"LSL error: {e}"))
            return

        data = []
        self.q.put(("status", "Recording…"))
        while not self.stopflag.is_set():
            sample, _ = inlet.pull_sample(timeout=0.1)
            if sample:
                fixed = sample[:FFT_MAX_HZ] if len(sample) >= FFT_MAX_HZ \
                        else sample + [0]*(FFT_MAX_HZ - len(sample))
                data.append(fixed)

        # save
        os.makedirs(self.save_dir, exist_ok=True)
        fname  = time.strftime("%Y%m%d_%H%M%S") + ".npy"
        fpath  = os.path.join(self.save_dir, fname)
        np.save(fpath, np.asarray(data))

        # send file path & sample count back to GUI
        self.q.put(("done", (fpath, len(data))))

    def stop(self):
        self.stopflag.set()

# ───────────────────────────────── GUI ──────────────────────────────────────
class CaptureGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("EEG Capture – Data Dave")
        self.resizable(False, False)

        # folder entry
        ttk.Label(self, text="Save folder:", padding=(5,10,0,0)) \
            .grid(row=0, column=0, sticky="w")
        self.path_var = tk.StringVar(value="data/")
        ttk.Entry(self, width=40, textvariable=self.path_var) \
            .grid(row=0, column=1, padx=5, pady=(10,0))
        ttk.Label(self, text="Please append the category after data/",
                  foreground="grey") \
            .grid(row=1, column=0, columnspan=2, sticky="w", padx=5)

        # record button
        self.rec_btn = ttk.Button(self, text="●  Record",
                                  style="Rec.TButton", command=self.toggle)
        self.rec_btn.grid(row=2, column=0, columnspan=2, pady=12, ipadx=10)
        ttk.Style(self).configure("Rec.TButton", foreground="red")

        # status label
        self.status = tk.StringVar(value="Idle")
        ttk.Label(self, textvariable=self.status) \
            .grid(row=3, column=0, columnspan=2, pady=(0,8))

        # internal
        self.worker: CaptureThread | None = None
        self.msg_q = queue.Queue()
        self.after(100, self.poll_q)

        # start live viewer in separate thread
        threading.Thread(target=start_live_viewer, daemon=True).start()

    # ── start/stop recording ────────────────────────────────────────────────
    def toggle(self):
        if self.worker is None:                      # start
            folder = self.path_var.get().strip()
            if not (folder.startswith("data/") and len(folder) > 5):
                messagebox.showerror("Folder error",
                                     "Enter something like data/walking")
                return
            self.worker = CaptureThread(folder, self.msg_q)
            self.worker.start()
            self.rec_btn.config(text="■  Stop")
            self.status.set("Connecting to LSL…")
        else:                                       # stop
            self.worker.stop()
            self.rec_btn.config(state="disabled")

    # ── queue poll ──────────────────────────────────────────────────────────
    def poll_q(self):
        try:
            kind, payload = self.msg_q.get_nowait()
            if kind == "status":
                self.status.set(payload)

            elif kind == "done":
                fpath, nsamp = payload
                self.status.set(f"Saved {nsamp} samples to {os.path.basename(fpath)}")
                # print summary to terminal
                print(f"[DONE] {nsamp} samples saved → {fpath}")
                try:
                    data = np.load(fpath)
                    print(f"       array shape: {data.shape}, dtype: {data.dtype}")
                except Exception as e:
                    print(f"[WARN] Could not load file to inspect: {e}")

                self.rec_btn.config(text="●  Record", state="normal")
                self.worker = None

            elif kind == "error":
                self.status.set(payload)
                messagebox.showerror("Runtime error", payload)
                self.rec_btn.config(text="●  Record", state="normal")
                self.worker = None

        except queue.Empty:
            pass
        self.after(100, self.poll_q)

# ────────────────────────────────── run ─────────────────────────────────────
if __name__ == "__main__":
    if sys.platform == "win32":
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass
    CaptureGUI().mainloop()
