import logging

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .utils import format_date, format_time

logger = logging.getLogger(__name__)


class BookingEmailService:

    @staticmethod
    def _build_context(booking):
        return {
            'booking': booking,
            'date_str': format_date(booking.requested_date),
            'time_str': format_time(booking.requested_date, booking.requested_time),
        }

    @staticmethod
    def send_visitor_received(booking):
        context = BookingEmailService._build_context(booking)
        try:
            html = render_to_string('emails/booking_visitor_received.html', context)
            send_mail(
                subject='Your Discovery Call Request — Zimplixio',
                message=strip_tags(html),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[booking.email],
                html_message=html,
                fail_silently=False,
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
            send_mail(
                subject=f'New Booking: {booking.name} — {date_str} {time_str}',
                message=strip_tags(html),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[admin_email],
                html_message=html,
                fail_silently=False,
            )
        except Exception:
            logger.exception('Failed to send admin booking notification email')

    @staticmethod
    def send_visitor_cancelled(booking):
        context = BookingEmailService._build_context(booking)
        try:
            html = render_to_string('emails/booking_visitor_cancelled.html', context)
            send_mail(
                subject='Your Discovery Call Request — Zimplixio',
                message=strip_tags(html),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[booking.email],
                html_message=html,
                fail_silently=False,
            )
        except Exception:
            logger.exception('Failed to send booking cancellation email to %s', booking.email)

    @staticmethod
    def send_visitor_confirmed(booking):
        context = BookingEmailService._build_context(booking)
        context['zoom_url'] = getattr(settings, 'ZOOM_MEETING_URL', '')
        try:
            html = render_to_string('emails/booking_visitor_confirmed.html', context)
            send_mail(
                subject='Your Discovery Call is Confirmed — Zimplixio',
                message=strip_tags(html),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[booking.email],
                html_message=html,
                fail_silently=False,
            )
        except Exception:
            logger.exception('Failed to send booking confirmation email to %s', booking.email)
