"""
utils.py
--------
Common helper functions used by many screens:
 - validation of text/date fields
 - some colour / font constants so all screens look the same
"""

import re
from datetime import datetime
from tkinter import messagebox

# ---------------- Colour / Font theme (used across the whole app) ----------------
BG_COLOR = "#f0f2f5"
SIDEBAR_COLOR = "#1f3a5f"
SIDEBAR_HOVER = "#2c4f7c"
ACCENT_COLOR = "#2e86de"
DANGER_COLOR = "#e74c3c"
SUCCESS_COLOR = "#27ae60"
WHITE = "#ffffff"
TEXT_COLOR = "#2d3436"

FONT_TITLE = ("Segoe UI", 18, "bold")
FONT_HEADING = ("Segoe UI", 13, "bold")
FONT_NORMAL = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 10, "bold")
FONT_BTN = ("Segoe UI", 10, "bold")


def is_empty(value):
    """Returns True if the text field is empty or only spaces."""
    return value is None or str(value).strip() == ""


def validate_not_empty(value, field_name):
    """Raises a simple message box error if field is empty. Returns True/False."""
    if is_empty(value):
        messagebox.showerror("Validation Error", f"{field_name} cannot be empty.")
        return False
    return True


def validate_date(value, field_name="Date"):
    """Checks the date is in YYYY-MM-DD format and is a real date."""
    if is_empty(value):
        messagebox.showerror("Validation Error", f"{field_name} cannot be empty.")
        return False
    try:
        datetime.strptime(value.strip(), "%Y-%m-%d")
        return True
    except ValueError:
        messagebox.showerror("Validation Error", f"{field_name} must be in YYYY-MM-DD format.")
        return False


def validate_number(value, field_name):
    """Checks value can be converted to a positive float (used for study hours)."""
    try:
        num = float(value)
        if num < 0:
            raise ValueError
        return True
    except ValueError:
        messagebox.showerror("Validation Error", f"{field_name} must be a valid positive number.")
        return False


def validate_int(value, field_name):
    """Checks value is a positive whole number (used for total topics)."""
    try:
        num = int(value)
        if num < 0:
            raise ValueError
        return True
    except ValueError:
        messagebox.showerror("Validation Error", f"{field_name} must be a whole number (0 or more).")
        return False


def only_letters_numbers_space(value):
    """Simple check used for subject/exam names - letters, numbers, spaces, - and & allowed."""
    return bool(re.match(r'^[A-Za-z0-9 \-&().]+$', value.strip()))
