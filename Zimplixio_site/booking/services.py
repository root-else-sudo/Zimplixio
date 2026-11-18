import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .calendar_invite import build_invite
from .utils import format_date, format_time, format_time_in_tz

logger = logging.getLogger(__name__)


def _send(subject, html, to, cc=None, invite=None, method='REQUEST'):
    """Send one HTML email, optionally carrying a calendar invitation.

    The invite is attached twice on purpose. Clients that understand
    `METHOD:` read the alternative part and offer Accept / Decline inline;
    the rest fall back to the `invite.ics` attachment, which still imports
    with one click. Sending only one of the two loses one group or the other.
    """
    message = EmailMultiAlternatives(
        subject=subject,
        body=strip_tags(html),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=to,
        cc=cc or None,
    )
    message.attach_alternative(html, 'text/html')
    if invite:
        content_type = 'text/calendar; charset=UTF-8; method=%s' % method
        message.attach_alternative(invite, content_type)
        message.attach('invite.ics', invite, content_type)
    message.send(fail_silently=False)


class BookingEmailService:

    @staticmethod
    def _build_context(booking):
        time_str = format_time(booking.requested_date, booking.requested_time)
        if booking.visitor_timezone:
            visitor_time_str = format_time_in_tz(
                booking.requested_date,
                booking.requested_time,
                booking.visitor_timezone,
            )
        else:
            visitor_time_str = time_str
        return {
            'booking': booking,
            'date_str': format_date(booking.requested_date),
            'time_str': time_str,
            'visitor_time_str': visitor_time_str,
            'duration_minutes': getattr(settings, 'BOOKING_DURATION_MINUTES', 30),
        }

    @staticmethod
    def send_visitor_received(booking):
        context = BookingEmailService._build_context(booking)
        try:
            html = render_to_string('emails/booking_visitor_received.html', context)
            _send(
                subject='Your Discovery Call Request — Zimplixio',
                html=html,
                to=[booking.email],
            )
        except Exception:
            logger.exception('Failed to send visitor booking acknowledgement to %s', booking.email)

    @staticmethod
    def send_admin_notification(booking):
        admin_email = getattr(settings, 'LEAD_NOTIFICATION_EMAIL', '')
        if not admin_email:
            return
        context = BookingEmailService._build_context(booking)
        date_str = context['date_str']
        time_str = context['time_str']
        site_url = getattr(settings, 'SITE_URL', '').rstrip('/')
        context['admin_url'] = f'{site_url}/zm-admin/booking/bookingrequest/{booking.pk}/change/'
        try:
            html = render_to_string('emails/booking_admin_notification.html', context)
            # Deliberately no invite: this fires the moment the form is
            # submitted, before the slot has been accepted. Putting an
            # unconfirmed meeting on a calendar is worse than not sending one.
            _send(
                subject=f'New Booking: {booking.name} — {date_str} {time_str}',
                html=html,
                to=[admin_email],
            )
        except Exception:
            logger.exception('Failed to send admin booking notification email')

    @staticmethod
    def send_visitor_cancelled(booking):
        context = BookingEmailService._build_context(booking)
        try:
            html = render_to_string('emails/booking_visitor_cancelled.html', context)
            _send(
                subject='Your Discovery Call Request — Zimplixio',
                html=html,
                to=[booking.email],
                # Retracts the event rather than leaving a dead meeting
                # sitting on the visitor's calendar.
                invite=build_invite(booking, method='CANCEL'),
                method='CANCEL',
            )
        except Exception:
            logger.exception('Failed to send booking cancellation email to %s', booking.email)

    @staticmethod
    def send_visitor_confirmed(booking):
        context = BookingEmailService._build_context(booking)
        context['zoom_url'] = getattr(settings, 'ZOOM_MEETING_URL', '')
        admin_email = getattr(settings, 'LEAD_NOTIFICATION_EMAIL', '')
        try:
            html = render_to_string('emails/booking_visitor_confirmed.html', context)
            _send(
                subject='Your Discovery Call is Confirmed — Zimplixio',
                html=html,
                to=[booking.email],
                # Copied in so the same invite lands on both calendars at the
                # moment the meeting becomes real.
                cc=[admin_email] if admin_email and admin_email != booking.email else None,
                invite=build_invite(booking, method='REQUEST'),
                method='REQUEST',
            )
        except Exception:
            logger.exception('Failed to send booking confirmation email to %s', booking.email)
