from datetime import datetime
from zoneinfo import ZoneInfo


def format_date(d):
    return d.strftime('%A, %B ') + str(d.day) + d.strftime(', %Y')


def format_time(d, t):
    dt = datetime.combine(d, t)
    return dt.strftime('%I:%M %p').lstrip('0') or '12:00 AM'


def format_time_in_tz(d, t, tz_str, fallback='America/New_York'):
    """Format a time (stored as Eastern) in the given IANA timezone string."""
    try:
        visitor_tz = ZoneInfo(tz_str) if tz_str else ZoneInfo(fallback)
    except Exception:
        visitor_tz = ZoneInfo(fallback)
    eastern = ZoneInfo('America/New_York')
    dt_eastern = datetime.combine(d, t, tzinfo=eastern)
    dt_local = dt_eastern.astimezone(visitor_tz)
    return dt_local.strftime('%I:%M %p %Z').lstrip('0') or '12:00 AM'
