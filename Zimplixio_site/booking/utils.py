from datetime import datetime
from zoneinfo import ZoneInfo

from django.conf import settings
from django.utils import timezone


def booking_tz():
    """The timezone availability is published in."""
    return ZoneInfo(getattr(settings, 'BOOKING_TIMEZONE', 'America/New_York'))


def today_in_booking_tz():
    """Today's date in the booking timezone, NOT the server's.

    Production runs UTC with no TZ set, so `date.today()` rolls over at
    19:00 Eastern. Availability is published in Eastern, so using the
    server's date hid the whole of the next day from 7pm every weeknight.
    Anything deciding "is this date still bookable" must use this.
    """
    return timezone.now().astimezone(booking_tz()).date()


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
