"""Utility functions"""

from datetime import datetime

HOURS = [
    "12:00 AM",
    "1:00 AM",
    "2:00 AM",
    "3:00 AM",
    "4:00 AM",
    "5:00 AM",
    "6:00 AM",
    "7:00 AM",
    "8:00 AM",
    "9:00 AM",
    "10:00 AM",
    "11:00 AM",
    "12:00 PM",
    "1:00 PM",
    "2:00 PM",
    "3:00 PM",
    "4:00 PM",
    "5:00 PM",
    "6:00 PM",
    "7:00 PM",
    "8:00 PM",
    "9:00 PM",
    "10:00 PM",
    "11:00 PM",
]
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def date_as_string() -> str:
    """Get the date as a string"""
    return datetime.now().strftime("%d-%m-%Y_%H-%M-%S")


def validate_json_input(file: str):
    """Validate json input value"""
    split_file = file.split(".")
    json_str = ".json"
    if len(split_file) == 1:
        return file + json_str
    assert len(split_file) == 2 and file.endswith(json_str)
    return file


def remove_unicode_characters(s: str) -> str:
    """Remove unicode characters"""
    return s.encode("ascii", errors="ignore").strip().decode("ascii")
