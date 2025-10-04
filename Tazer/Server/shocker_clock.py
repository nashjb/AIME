import re
from typing import Optional
from obsidian_parser.note import DataviewInlineField

class ShockerClock:
    """
    Simple container for a dataview-style inline 'clock' field.
    Example value:
        "2025-10-03T09:44:51--2025-10-03T10:32:55"
    """
    # Keep separator in one place in case you change it later
    RANGE_SEPARATOR: str = "--"

    key: str
    value: str
    startTime: Optional[str]
    endTime: Optional[str]
    line_number: int
    raw_value: Optional[str]  # Original value with any formatting (may be None)

    def __init__(
        self,
        key: str,
        value: str,
        line_number: int,
        raw_value: Optional[str] = None,
        startTime: Optional[str] = None,
        endTime: Optional[str] = None,
    ) -> None:
        self.key = key
        self.value = value
        self.line_number = int(line_number)
        self.raw_value = raw_value if raw_value is not None else value
        self.startTime = startTime
        self.endTime = endTime

    @classmethod
    def from_dataviewinline(cls, field: "DataviewInlineField") -> "ShockerClock":
        """
        Build a Clock from a DataviewInlineField.
        Expects attributes: key, value, line_number, raw_value (optional).
        Parses startTime/endTime from value if formatted as 'start--end'.
        """
        field_key: str = str(getattr(field, "key", "")).strip()
        field_value_raw: str = str(getattr(field, "value", "")).strip()
        field_line_number: int = int(getattr(field, "line_number", -1))
        field_raw_value: Optional[str] = getattr(field, "raw_value", None)

        # Some parsers may leave a stray trailing ']' in raw_value; strip it safely.
        if field_raw_value is not None:
            field_raw_value = field_raw_value.strip()
            if field_raw_value.endswith("]") and not field_value_raw.endswith("]"):
                # only strip if it looks like an accidental carry-over
                field_raw_value = field_raw_value[:-1]

        # Parse start/end from the value (format: "<isoStart>--<isoEnd>")
        parsed_start_time: Optional[str] = None
        parsed_end_time: Optional[str] = None

        if cls.RANGE_SEPARATOR in field_value_raw:
            start_part, end_part = field_value_raw.split(cls.RANGE_SEPARATOR, 1)
            parsed_start_time = start_part.strip() or None
            parsed_end_time = end_part.strip() or None
        else:
            # If only one timestamp is present, treat it as startTime
            parsed_start_time = field_value_raw or None

        return cls(
            key=field_key,
            value=field_value_raw,
            line_number=field_line_number,
            raw_value=field_raw_value,
            startTime=parsed_start_time,
            endTime=parsed_end_time,
        )

    def __repr__(self) -> str:
        return (
            "Clock("
            f"key={self.key!r}, "
            f"value={self.value!r}, "
            f"startTime={self.startTime!r}, "
            f"endTime={self.endTime!r}, "
            f"line_number={self.line_number}, "
            f"raw_value={self.raw_value!r})"
        )
