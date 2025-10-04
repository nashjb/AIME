import re
from datetime import datetime
from typing import Optional, Dict, Callable
from obsidian_parser import Note, WikiLink # if you still use it
from obsidian_parser.note import Task, DataviewInlineField
from shocker_clock import ShockerClock
from datetime import datetime, date


class ShockerTask:
    TAG_PAIR_RE   = re.compile(r"\[(\w+)::\s*((?:\[\[.*?\]\])|(?:[^\[\]]+))\s*\]")
    TIME_RANGE_RE = re.compile(r'^\s*(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})(?:\s+(.*))?$')
    TIME_ONLY_RE  = re.compile(r'^\s*(\d{1,2}:\d{2})(?:\s+(.*))?$')
    VIBRATED = "vibrated"
    SHOCKED = "shocked"

    def __init__(
        self,
        status: str,
        text: str,
        note: Note,
        raw_text: str,
        line_number: int,
        startTime: Optional[datetime] = None,
        endTime: Optional[datetime] = None,
        fields: Optional[[DataviewInlineField]] = None
    ):
        self.status = status
        self.raw_text = raw_text
        self.text = text
        self.note = note
        self.startTime = startTime
        self.endTime = endTime
        self.fields = fields or {}
        self.line_number = line_number

    @property
    def clockRunning(self) -> bool:
        """True if now is between start and end, and task not done."""
        if not self.startTime or not self.endTime:
            return False
        now = datetime.now()
        return self.startTime <= now <= self.endTime and not self.done
    
    @property
    def vibrated(self) -> DataviewInlineField | None:
        for f in self.fields:
            if f.key == self.VIBRATED:
                return f
        return None
    
    @property
    def isVibrated(self) -> bool | None:
        # Here I need to check if it is there or null
        vibrated_property = self.vibrated

        if vibrated_property:   
            return str(vibrated_property.value).strip().lower() == "true"
        else:
            return None

    
    @property
    def shocked(self) -> DataviewInlineField | None:
        for f in self.fields:
            if f.key == self.SHOCKED:
                return f
        return None   


    def setVibrate(self, done: bool, rebuild: Callable[[], None]) -> None:
        # here I need to check the fields to see if the vibrated field exist
        value_string = "true" if done else "false"
        content_to_write = f"[vibrated:: {value_string}]"
        vibrated_property = self.vibrated

        if vibrated_property:   
            print("Found")
            self.replace_line(vibrated_property.line_number + 1, content_to_write, 4)
        else:
            print("Not found:   " + str(self.line_number + 1))
            self.insert_line_at(self.line_number + 1, content_to_write, 4)

        rebuild()


    @property
    def clocks(self) -> "[ShockerClock]":
        """True if now is between start and end, and task not done."""
        clocks = []
        for field in self.fields:
            clocks.append(ShockerClock.from_dataviewinline(field))
        return clocks

    @property
    def done(self) -> bool:
        """Task completed if status is x/X."""
        return self.status.lower() == "x"

    @classmethod
    def from_task(cls, task: Task, note: Note, offset: int) -> "ShockerTask":
        # fields on the line right after the task
        task_line = offset + task.line_number
        print("From Task Number:    " + str(task_line))
        target_line_number: int = task_line + 1
        dataview_inline_fields: list[DataviewInlineField] = []

        # copy dataview fields from the next line
        for dataview_field in sorted(note.dataview_fields, key=lambda x: x.line_number):
            if dataview_field.line_number == target_line_number:
                dataview_inline_fields.append(
                    DataviewInlineField(
                        key=dataview_field.key.replace('[', '').replace(']', ''),
                        value=dataview_field.value.replace('[', '').replace(']', ''),
                        line_number=target_line_number,
                        raw_value=getattr(dataview_field, "raw_value", None),
                    )
                )

        # parse inline k:: v on the task line, and add them too
        inline_key_value_pairs: dict[str, str] = {
            key: value.strip() for key, value in cls.TAG_PAIR_RE.findall(task.text)
        }
        for key, value in inline_key_value_pairs.items():
            dataview_inline_fields.append(
                DataviewInlineField(
                    key=key.replace('[', '').replace(']', ''),
                    value=value,
                    line_number=task_line,
                    raw_value=f"{key}::{value}",
                )
            )

        # clean task text (remove inline [k:: v] tags)
        clean_text: str = cls.TAG_PAIR_RE.sub("", task.text).strip()

        # defaults for optional times
        start_time: str | None = None
        end_time: str | None = None

        # try to parse "HH:MM - HH:MM Description"
        time_range_match = cls.TIME_RANGE_RE.match(clean_text)
        if time_range_match:
            parsed_start_str, parsed_end_str, parsed_description = time_range_match.groups()
            start_time = datetime.combine(date.today(), datetime.strptime(parsed_start_str, "%H:%M").time())
            end_time   = datetime.combine(date.today(), datetime.strptime(parsed_end_str, "%H:%M").time())
            # if there is a description, use it as the clean text; otherwise blank
            clean_text = (parsed_description or "").strip()
        else:
            # try to parse "HH:MM Description"
            time_only_match = cls.TIME_ONLY_RE.match(clean_text)
            if time_only_match:
                parsed_start_time, parsed_description = time_only_match.groups()
                start_time = parsed_start_time
                clean_text = (parsed_description or "").strip()

        return cls(
            status=task.status,
            raw_text=task.text,
            text=clean_text,
            note=note,
            startTime=start_time,
            endTime=end_time,
            fields=dataview_inline_fields,
            line_number=task.line_number,
        )

    def insert_line_at(self, line_index: int, content: str, indent_spaces: int = 4) -> int:
        # read whole file
        file_text = self.note.path.read_text(encoding="utf-8")

        # keep the file’s newline style
        newline = "\r\n" if "\r\n" in file_text else "\n"

        # split into lines (no endings) and clamp index
        lines = file_text.splitlines()
        if line_index < 0:
            line_index = 0
        if line_index > len(lines):
            line_index = len(lines)

        # insert
        indent = " " * indent_spaces
        lines.insert(line_index, f"{indent}{content}")

        # write back and sync in-memory
        new_text = newline.join(lines)
        self.note.path.write_text(new_text, encoding="utf-8")
        self.note._raw_content = new_text
        return line_index


    def replace_line(self, line_index: int, content: str, indent_spaces: int = 4) -> int:
        # read whole file
        file_text = self.note.path.read_text(encoding="utf-8")
        newline = "\r\n" if "\r\n" in file_text else "\n"
        lines = file_text.splitlines()

        # replace (no extra error checks)
        indent = " " * indent_spaces
        lines[line_index] = f"{indent}{content}"

        # write back and sync in-memory
        new_text = newline.join(lines)
        self.note.path.write_text(new_text, encoding="utf-8")
        self.note._raw_content = new_text
        return line_index
