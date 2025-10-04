from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
import sys

# ======= CONFIG (edit these) =======
TOTAL_SECONDS   = 30 * 60       # e.g. 45 minutes
TITLE_TEXT      = "Task 1 — Deep Work"
LAG_SECONDS     = 5 * 60        # shows as +MM:SS (can be negative)
CLOCK_COLOR     = "#00cc00"     # single fixed color for the clock (no overrides)
ALWAYS_ON_TOP   = True
AUTO_START      = True
# ===================================

def _fmt_hms(sec: int) -> str:
    sec = max(0, int(sec))
    h = sec // 3600
    m = (sec % 3600) // 60
    s = sec % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

def _fmt_mmss_signed(sec: int) -> str:
    sign = "+" if sec >= 0 else "-"
    sec = abs(int(sec))
    m = sec // 60
    s = sec % 60
    return f"{sign}{m:02d}:{s:02d}"

class CountdownWindow(QWidget):
    def __init__(self,
                 total_seconds: int,
                 title_text: str = "",
                 lag_seconds: int = 0,
                 clock_color: str = "#000000",
                 always_on_top: bool = True,
                 auto_start: bool = True):
        super().__init__()

        self.total = int(total_seconds)
        self.remaining = int(total_seconds)
        self._lag = int(lag_seconds)
        self._clock_color = clock_color

        self.setWindowTitle("Countdown")
        if always_on_top:
            self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        self.resize(520, 220)

        # Big clock (HH:MM:SS)
        self.clock = QLabel(_fmt_hms(self.remaining))
        self.clock.setAlignment(Qt.AlignCenter)
        # color will be applied via _apply_color()
        self.clock.setStyleSheet("font-family: Consolas; font-size: 72px; font-weight: 800;")

        # Title (below clock)
        self.title = QLabel(title_text or "")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("font-size: 18px; color: #444;")

        # Lag (+MM:SS)
        self.lag = QLabel(_fmt_mmss_signed(self._lag))
        self.lag.setAlignment(Qt.AlignCenter)
        self.lag.setStyleSheet("font-family: Consolas; font-size: 24px; font-weight: 700; color: #0077cc;")

        layout = QVBoxLayout(self)
        layout.addWidget(self.clock)
        layout.addWidget(self.title)
        layout.addWidget(self.lag)

        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._tick)

        self._apply_color()
        if auto_start:
            self.start()

    # --- Controls you can call later if needed ---
    def start(self): self._timer.start()
    def pause(self): self._timer.stop()
    def reset(self, total_seconds: int = None):
        if total_seconds is not None:
            self.total = int(total_seconds)
        self.remaining = self.total
        self.clock.setText(_fmt_hms(self.remaining))
        self._apply_color()

    def set_title(self, text: str): self.title.setText(text or "")
    def set_lag(self, lag_seconds: int):
        self._lag = int(lag_seconds)
        self.lag.setText(_fmt_mmss_signed(self._lag))

    # --- Internals ---
    def _apply_color(self):
        # always apply the single configured color
        self.clock.setStyleSheet(f"font-family: Consolas; font-size: 72px; font-weight: 800; color: {self._clock_color};")

    def _tick(self):
        if self.remaining > 0:
            self.remaining -= 1
            if self.remaining in (600, 60, 10):  # optional warnings: 10m, 1m, 10s
                QApplication.beep()
            self.clock.setText(_fmt_hms(self.remaining))
            # color remains the same; keep calling to be consistent
            self._apply_color()
        else:
            self._timer.stop()
            QApplication.beep(); QApplication.beep()  # finished

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = CountdownWindow(
        total_seconds=TOTAL_SECONDS,
        title_text=TITLE_TEXT,
        lag_seconds=LAG_SECONDS,
        clock_color=CLOCK_COLOR,
        always_on_top=ALWAYS_ON_TOP,
        auto_start=AUTO_START
    )
    w.show()
    sys.exit(app.exec_())
