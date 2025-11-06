# api/utils/week_utils.py
from datetime import datetime
import calendar


def extract_year_month_week(d):
    """
    Returns (year, month, week_identifier).
    week_identifier is ISO week number (string) but when saving files we keep it human friendly.
    """
    if isinstance(d, str):
        d = datetime.fromisoformat(d)
    year = d.isocalendar().year
    week = d.isocalendar().week
    month = d.month
    # use week as 2-digit string for filenames
    return year, month, f"week-{week:02d}"
