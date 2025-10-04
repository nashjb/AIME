import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, date as date_cls
from typing import Optional, Dict, Any, List, Tuple

from obsidian_parser import Note, WikiLink  # WikiLink kept if you use it elsewhere

# ---------- Parsing helpers ----------
TIME_FMT = "%H:%M"
ISO_DT = "%Y-%m-%dT%H:%M:%S"

TAG_PAIR_RE = re.compile(r"\[(\w+)::\s*((?:\[\[.*?\]\])|(?:[^\[\]]+))\s*\]")
TASK_START_RE = re.compile(r"^\s*[-*]\s*\[(?: |x|X)\]")
CLOCK_LINE_RE = re.compile(
    r"^\s*\[clock::\s*(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})\s*--\s*"
    r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})\s*\]\s*$"
)

def _parse_time_hhmm(s: str) -> Optional[datetime]:
    if not s:
        return None
    try:
        hhmm = datetime.strptime(s.strip(), TIME_FMT)
        base = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        return base.replace(hour=hhmm.hour, minute=hhmm.minute)
    except Exception as e:
        print(f"[ERROR] Failed to parse time '{s}': {e}")
        return None

def _parse_duration_minutes(s: str) -> Optional[int]:
    """Accepts '2h', '90m', '1h30m', '45min', '45mins', or plain '90' (minutes)."""
    if not s:
        return None
    txt = s.strip().lower().replace(" ", "")
    try:
        m = re.fullmatch(r"(?:(\d+)h)?(?:(\d+)m(?:in|ins)?)?", txt)
        if m:
            return (int(m.group(1) or 0) * 60) + int(m.group(2) or 0)
        if txt.isdigit():
            return int(txt)
    except Exception as e:
        print(f"[ERROR] Failed to parse duration '{s}': {e}")
    return None


@dataclass(slots=True)
class ShockerTask:
    status: str
    text: str
    note: Note
    due: Optional[str] = None
    time: Optional[str] = None
    date: Optional[str] = None
    failed: Optional[str] = None
    end: Optional[str] = None
    duration: Optional[str] = None
    clock_intervals: List[Tuple[str, str]] = field(default_factory=list)
    extra_notes: List[str] = field(default_factory=list)
    completed_on: Optional[str] = None

    custom_fields: Dict[str, Any] = field(default_factory=dict)
    line_number: Optional[int] = None
    indent_level: int = 0

    @classmethod
    def from_task(cls, task: "Task", note: Note) -> "ShockerTask":
        try:
            fields = {k: v.strip() for k, v in TAG_PAIR_RE.findall(task.text)}
            clean_text = TAG_PAIR_RE.sub("", task.text).strip()
        except Exception as e:
            print(f"[ERROR] Failed parsing fields for task '{task}': {e}")
            fields, clean_text = {}, task.text

        inst = cls(
            status=task.status,
            text=clean_text,
            note=note,
            due=fields.get("due"),
            time=fields.get("time"),
            failed=fields.get("failed"),
            date=fields.get("date").strip("[]") if fields.get("date") else None,
            end=fields.get("end"),
            duration=fields.get("duration"),
            custom_fields={k: v for k, v in fields.items()
                           if k not in {"due", "time", "date", "end", "duration", "failed"}},
            line_number=getattr(task, "line_number", None),
            indent_level=getattr(task, "indent_level", 0),
        )

        if inst.status.lower() == "x":
            inst.completed_on = datetime.today().strftime("%Y-%m-%d")

        if inst.line_number is not None:
            try:
                content = inst.note.path.read_text(encoding="utf-8")
                lines = content.splitlines()
                for i, line in enumerate(lines[inst.line_number + 1:], start=inst.line_number + 1):
                    if TASK_START_RE.search(line):
                        break
                    if not line.strip():
                        continue
                    m = CLOCK_LINE_RE.match(line)
                    if m:
                        inst.clock_intervals.append((m.group(1), m.group(2)))
                    else:
                        inst.extra_notes.append(line)
            except Exception as e:
                print(f"[ERROR] Failed scanning block under task '{inst.text}': {e}")

        return inst

    def _time_prefix(self) -> str:
        start_dt = _parse_time_hhmm(self.time) if self.time else None
        end_dt = _parse_time_hhmm(self.end) if self.end else None
        if not end_dt and self.duration and start_dt:
            mins = _parse_duration_minutes(self.duration)
            if mins:
                end_dt = start_dt + timedelta(minutes=mins)

        if start_dt and end_dt:
            return f"{start_dt.strftime(TIME_FMT)} - {end_dt.strftime(TIME_FMT)} "
        if start_dt:
            return f"{start_dt.strftime(TIME_FMT)} "
        return ""

    def __str__(self) -> str:
        checkbox = "x" if self.status.lower() == "x" else " "
        suffix = f" ✅ {self.completed_on}" if (self.completed and self.completed_on) else ""
        main = f"- [{checkbox}] {self._time_prefix()}{self.text}{suffix}"
        block = [f"      [clock::{s}--{e}]" for s, e in self.clock_intervals] + self.extra_notes
        return "\n".join([main] + block) if block else main

    def mark_failed(self) -> None:
        if self.line_number is None or not self.note:
            print("[ERROR] Cannot mark failed: missing line_number or note")
            return
        try:
            lines = self.note.path.read_text(encoding="utf-8").splitlines()
            if self.line_number >= len(lines):
                print(f"[ERROR] Line number {self.line_number} out of range")
                return
            line = lines[self.line_number]
            if self.text.strip() not in line:
                print(f"[WARN] Task text '{self.text}' not found in expected line")
            if "[failed::" in line:
                print(f"[INFO] Task already marked failed: {line}")
                return
            lines[self.line_number] = line.rstrip() + " [failed:: true]"
            self.note.path.write_text("\n".join(lines), encoding="utf-8")
            self.note._raw_content = "\n".join(lines)
            print(f"[SUCCESS] Marked task '{self.text}' as failed")
        except Exception as e:
            print(f"[ERROR] Failed to mark task failed: {e}")

    @property
    def completed(self) -> bool:
        return self.status.lower() == "x"

    def mark_completed(self, when: Optional[date_cls] = None) -> None:
        if self.line_number is None or not self.note:
            print("[ERROR] Cannot mark completed: missing line_number or note")
            return
        try:
            stamp = (when or date_cls.today()).strftime("%Y-%m-%d")
            lines = self.note.path.read_text(encoding="utf-8").splitlines()
            if self.line_number >= len(lines):
                print(f"[ERROR] Line number {self.line_number} out of range")
                return
            line = re.sub(r"^(\s*[-*]\s*\[)\s(\]\s*)", r"\1x\2", lines[self.line_number])
            if f"✅ {stamp}" not in line:
                line = line.rstrip() + f" ✅ {stamp}"
            lines[self.line_number] = line
            self.note.path.write_text("\n".join(lines), encoding="utf-8")
            self.note._raw_content = "\n".join(lines)
            self.status, self.completed_on = "x", stamp
            print(f"[SUCCESS] Marked task '{self.text}' completed on {stamp}")
        except Exception as e:
            print(f"[ERROR] Failed to mark completed: {e}")

    def add_clock_interval(self, start: datetime, end: datetime) -> None:
        if self.line_number is None or not self.note:
            print("[ERROR] Cannot add clock: missing line_number or note")
            return
        try:
            s_iso, e_iso = start.strftime(ISO_DT), end.strftime(ISO_DT)
            lines = self.note.path.read_text(encoding="utf-8").splitlines()
            lines.insert(self.line_number + 1, f"      [clock::{s_iso}--{e_iso}]")
            self.note.path.write_text("\n".join(lines), encoding="utf-8")
            self.note._raw_content = "\n".join(lines)
            self.clock_intervals.append((s_iso, e_iso))
            print(f"[SUCCESS] Added clock interval to task '{self.text}'")
        except Exception as e:
            print(f"[ERROR] Failed to add clock interval: {e}")

    def total_clock_minutes(self) -> int:
        total = 0
        for s_iso, e_iso in self.clock_intervals:
            try:
                s, e = datetime.strptime(s_iso, ISO_DT), datetime.strptime(e_iso, ISO_DT)
                total += int((e - s).total_seconds() // 60)
            except Exception as e:
                print(f"[WARN] Skipping bad clock interval {s_iso}--{e_iso}: {e}")
        return total
