"""iCalendar (RFC 5545) invitations for confirmed discovery calls.

A confirmed booking goes out with a `text/calendar` part carrying
`METHOD:REQUEST`, which is what makes a mail client show Accept / Tentative
/ Decline instead of a plain attachment. Cancelling sends `METHOD:CANCEL`
for the same UID, so the meeting is retracted from the visitor's calendar
rather than left sitting there.

Two things here are easy to get wrong and are covered by tests:

- **The timezone.** `requested_date` and `requested_time` are naive values
  that *mean* Eastern (see `booking.utils`). DTSTART must be a UTC instant,
  so the two are combined with the booking timezone attached and only then
  converted. Combining them naively is the same class of bug that hid a day
  of availability every evening; here it would put every invite five hours
  off, in silence.
- **The line format.** RFC 5545 counts octets, not characters, caps a line
  at 75 of them, and requires CRLF. A long Zoom URL overruns that on its
  own, and an unescaped comma truncates the field it sits in.

This deliberately does not talk to Zoom or to any calendar API. The event
carries the static `ZOOM_MEETING_URL`, the same link the email already
shows. Per-meeting links and a calendar that tracks RSVPs server-side would
both need API credentials -- a separate piece of work.
"""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from django.conf import settings

from .utils import booking_tz

# The domain that owns the UID namespace. Changing this orphans every invite
# already sitting in a visitor's calendar, because a UID is how a client
# decides whether an update refers to an event it already has.
UID_DOMAIN = 'zimplixio.com'

PRODID = '-//Zimplixio//Booking//EN'
SUMMARY = 'Discovery Call - Zimplixio'

# A cancellation has to outrank the request it supersedes, or clients ignore it.
_SEQUENCE = {'REQUEST': 0, 'CANCEL': 1}
_STATUS = {'REQUEST': 'CONFIRMED', 'CANCEL': 'CANCELLED'}


def _escape(value):
    """Escape a TEXT value. Backslash first, or we escape our own escapes."""
    return (
        str(value)
        .replace('\\', '\\\\')
        .replace(';', '\\;')
        .replace(',', '\\,')
        .replace('\r\n', '\\n')
        .replace('\n', '\\n')
        .replace('\r', '\\n')
    )


def _quote_param(value):
    """A parameter value containing a comma, colon or semicolon must be quoted.

    There is no escape mechanism inside a quoted parameter, so an embedded
    double quote can only be dropped.
    """
    return '"%s"' % str(value).replace('"', '')


def _fold(line):
    """Fold to 75 octets per RFC 5545, continuations prefixed with a space.

    Measured in octets rather than characters so a non-ASCII name cannot
    push a line over the limit, and split on character boundaries so a
    multi-byte sequence is never cut in half.
    """
    chunks = []
    current = ''
    for char in line:
        candidate_len = len(current.encode('utf-8')) + len(char.encode('utf-8'))
        if candidate_len > 75:
            chunks.append(current)
            current = ' ' + char
        else:
            current += char
    chunks.append(current)
    return '\r\n'.join(chunks)


def _utc(d, t):
    """A naive Eastern date+time as an aware UTC datetime."""
    return datetime.combine(d, t, tzinfo=booking_tz()).astimezone(ZoneInfo('UTC'))


def _stamp(dt):
    return dt.strftime('%Y%m%dT%H%M%SZ')


def event_uid(booking):
    """Stable across every message about this booking. Never recomputed."""
    return 'booking-%s@%s' % (booking.pk, UID_DOMAIN)


def _description(booking, zoom_url):
    lines = ['Discovery call with %s.' % booking.name]
    if zoom_url:
        lines.append('')
        lines.append('Join: %s' % zoom_url)
    if booking.message:
        lines.append('')
        lines.append('What you told us:')
        lines.append(booking.message)
    return '\n'.join(lines)


def build_invite(booking, method='REQUEST'):
    """The .ics body for a booking, as a REQUEST or a CANCEL."""
    if method not in _SEQUENCE:
        raise ValueError('method must be REQUEST or CANCEL, got %r' % method)

    zoom_url = getattr(settings, 'ZOOM_MEETING_URL', '') or ''
    duration = getattr(settings, 'BOOKING_DURATION_MINUTES', 30)
    organizer = settings.DEFAULT_FROM_EMAIL
    admin_email = getattr(settings, 'LEAD_NOTIFICATION_EMAIL', '') or ''

    start = _utc(booking.requested_date, booking.requested_time)
    end = start + timedelta(minutes=duration)
    now = datetime.now(ZoneInfo('UTC'))

    lines = [
        'BEGIN:VCALENDAR',
        'VERSION:2.0',
        'PRODID:%s' % PRODID,
        'CALSCALE:GREGORIAN',
        'METHOD:%s' % method,
        'BEGIN:VEVENT',
        'UID:%s' % event_uid(booking),
        'SEQUENCE:%d' % _SEQUENCE[method],
        'DTSTAMP:%s' % _stamp(now),
        'DTSTART:%s' % _stamp(start),
        'DTEND:%s' % _stamp(end),
        'SUMMARY:%s' % _escape(SUMMARY),
        'DESCRIPTION:%s' % _escape(_description(booking, zoom_url)),
    ]

    if zoom_url:
        lines.append('LOCATION:%s' % _escape(zoom_url))

    lines.append('ORGANIZER;CN=%s:mailto:%s' % (_quote_param('Zimplixio'), organizer))
    lines.append(
        'ATTENDEE;CN=%s;ROLE=REQ-PARTICIPANT;PARTSTAT=NEEDS-ACTION;RSVP=TRUE:mailto:%s'
        % (_quote_param(booking.name), booking.email)
    )
    # Both parties belong on the event, so each side's calendar names the other.
    if admin_email and admin_email != booking.email:
        lines.append(
            'ATTENDEE;CN=%s;ROLE=REQ-PARTICIPANT;PARTSTAT=ACCEPTED;RSVP=FALSE:mailto:%s'
            % (_quote_param('Zimplixio'), admin_email)
        )

    lines += [
        'STATUS:%s' % _STATUS[method],
        'END:VEVENT',
        'END:VCALENDAR',
    ]

    return '\r\n'.join(_fold(line) for line in lines) + '\r\n'
