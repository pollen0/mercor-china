"""
Date parsing utility for converting string dates to Date objects.
Handles various formats like "Fall 2022", "Spring 2024", "2022-09", "Present", etc.
"""
import re
from datetime import date
from typing import Optional, Tuple


# Season to month mapping (start month of each season)
SEASON_MONTHS = {
    "spring": 1,     # Jan-May
    "summer": 5,     # May-Aug
    "fall": 9,       # Sep-Dec
    "autumn": 9,
    "winter": 1,     # Jan (typically winter semester)
}

# Month name mapping
MONTH_NAMES = {
    "january": 1, "jan": 1,
    "february": 2, "feb": 2,
    "march": 3, "mar": 3,
    "april": 4, "apr": 4,
    "may": 5,
    "june": 6, "jun": 6,
    "july": 7, "jul": 7,
    "august": 8, "aug": 8,
    "september": 9, "sep": 9, "sept": 9,
    "october": 10, "oct": 10,
    "november": 11, "nov": 11,
    "december": 12, "dec": 12,
}


def parse_date_string(date_str: Optional[str]) -> Tuple[Optional[date], bool]:
    """
    Parse a date string into a Date object.

    Args:
        date_str: Date string in various formats:
            - "Fall 2022", "Spring 2024"
            - "2022-09", "09/2022", "Sep 2022"
            - "2022-09-15" (ISO format)
            - "Present", "Current", "Now"
            - "2022"

    Returns:
        Tuple of (parsed_date, is_current)
        - parsed_date: Date object or None if parsing failed
        - is_current: True if the date represents "Present" or "Current"
    """
    if not date_str:
        return None, False

    date_str = date_str.strip().lower()

    # Check for "Present" / "Current" / "Now"
    if date_str in ("present", "current", "now", "ongoing", "today"):
        return date.today(), True

    # Try ISO format: YYYY-MM-DD
    iso_match = re.match(r'^(\d{4})-(\d{1,2})-(\d{1,2})$', date_str)
    if iso_match:
        year, month, day = int(iso_match.group(1)), int(iso_match.group(2)), int(iso_match.group(3))
        try:
            return date(year, month, day), False
        except ValueError:
            pass

    # Try YYYY-MM format
    ym_match = re.match(r'^(\d{4})-(\d{1,2})$', date_str)
    if ym_match:
        year, month = int(ym_match.group(1)), int(ym_match.group(2))
        try:
            return date(year, month, 1), False
        except ValueError:
            pass

    # Try MM/YYYY or M/YYYY format
    mm_yyyy_match = re.match(r'^(\d{1,2})/(\d{4})$', date_str)
    if mm_yyyy_match:
        month, year = int(mm_yyyy_match.group(1)), int(mm_yyyy_match.group(2))
        try:
            return date(year, month, 1), False
        except ValueError:
            pass

    # Try "Season YYYY" format (e.g., "Fall 2022", "Spring 2024")
    season_match = re.match(r'^(spring|summer|fall|autumn|winter)\s*(\d{4})$', date_str)
    if season_match:
        season, year = season_match.group(1), int(season_match.group(2))
        month = SEASON_MONTHS.get(season, 1)
        try:
            return date(year, month, 1), False
        except ValueError:
            pass

    # Try "Month YYYY" format (e.g., "September 2022", "Sep 2022")
    for month_name, month_num in MONTH_NAMES.items():
        month_year_match = re.match(rf'^{month_name}\.?\s*(\d{{4}})$', date_str)
        if month_year_match:
            year = int(month_year_match.group(1))
            try:
                return date(year, month_num, 1), False
            except ValueError:
                pass

    # Try just year: YYYY
    year_match = re.match(r'^(\d{4})$', date_str)
    if year_match:
        year = int(year_match.group(1))
        try:
            return date(year, 1, 1), False
        except ValueError:
            pass

    # Try "YYYY Season" format (e.g., "2022 Fall")
    year_season_match = re.match(r'^(\d{4})\s*(spring|summer|fall|autumn|winter)$', date_str)
    if year_season_match:
        year, season = int(year_season_match.group(1)), year_season_match.group(2)
        month = SEASON_MONTHS.get(season, 1)
        try:
            return date(year, month, 1), False
        except ValueError:
            pass

    # Could not parse
    return None, False


def format_relative_date(dt: date) -> str:
    """
    Format a date as a relative string like "2 weeks ago", "3 months ago".

    Args:
        dt: Date to format

    Returns:
        Human-readable relative date string
    """
    today = date.today()
    delta = today - dt
    days = delta.days

    if days < 0:
        return "in the future"
    elif days == 0:
        return "today"
    elif days == 1:
        return "yesterday"
    elif days < 7:
        return f"{days} days ago"
    elif days < 14:
        return "1 week ago"
    elif days < 30:
        weeks = days // 7
        return f"{weeks} weeks ago"
    elif days < 60:
        return "1 month ago"
    elif days < 365:
        months = days // 30
        return f"{months} months ago"
    elif days < 730:
        return "1 year ago"
    else:
        years = days // 365
        return f"{years} years ago"
