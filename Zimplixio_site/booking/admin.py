import logging
from datetime import datetime

from django.conf import settings
from django.contrib import admin
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .models import BookingRequest, TimeSlot

logger = logging.getLogger(__name__)


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['day_of_week', 'start_time', 'end_time', 'is_active']
    list_filter = ['day_of_week', 'is_active']


@admin.register(BookingRequest)
class BookingRequestAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'requested_date', 'requested_time', 'status', 'created_at']
    list_filter = ['status', 'requested_date']
    list_editable = ['status']
    search_fields = ['name', 'email', 'company']

    def save_model(self, request, obj, form, change):
        if change and obj.pk:
            try:
                old_status = BookingRequest.objects.get(pk=obj.pk).status
            except BookingRequest.DoesNotExist:
                old_status = None
            if old_status != 'confirmed' and obj.status == 'confirmed':
                super().save_model(request, obj, form, change)
                self._send_confirmation_email(obj)
                return
        super().save_model(request, obj, form, change)

    def _send_confirmation_email(self, booking):
        d = booking.requested_date
        date_str = d.strftime('%A, %B ') + str(d.day) + d.strftime(', %Y')
        dt = datetime.combine(d, booking.requested_time)
        time_str = dt.strftime('%I:%M %p').lstrip('0') or '12:00 AM'
        context = {'booking': booking, 'date_str': date_str, 'time_str': time_str}
        try:
            html = render_to_string('emails/booking_visitor_confirmed.html', context)
            send_mail(
                subject='Your Discovery Call is Confirmed — Zimplixio',
                message=strip_tags(html),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[booking.email],
                html_message=html,
                fail_silently=True,
            )
        except Exception:
            logger.exception('Failed to send booking confirmation email to %s', booking.email)
