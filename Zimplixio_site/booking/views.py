import calendar
import logging
from datetime import date, datetime, timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.html import strip_tags
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_GET
from django.views.generic import TemplateView, CreateView
from django_ratelimit.decorators import ratelimit

from .forms import BookingForm
from .models import BookingRequest, TimeSlot

logger = logging.getLogger(__name__)


def _generate_slot_times(slots):
    """Return sorted list of time objects at 30-min intervals across all given TimeSlots."""
    times = set()
    for slot in slots:
        current = datetime.combine(datetime.today(), slot.start_time)
        end = datetime.combine(datetime.today(), slot.end_time)
        while current < end:
            times.add(current.time())
            current += timedelta(minutes=30)
    return sorted(times)


@require_GET
def available_days_view(request):
    """Return which calendar days in a given month have available slots."""
    month_str = request.GET.get('month', '')
    try:
        year, month = [int(x) for x in month_str.split('-')]
        date(year, month, 1)  # validate
    except (ValueError, AttributeError):
        return JsonResponse({'error': 'Invalid month. Use YYYY-MM.'}, status=400)

    active_weekdays = set(
        TimeSlot.objects.filter(is_active=True).values_list('day_of_week', flat=True)
    )

    # Confirmed bookings this month keyed by (date, time)
    confirmed = set(
        BookingRequest.objects.filter(
            requested_date__year=year,
            requested_date__month=month,
            status='confirmed',
        ).values_list('requested_date', 'requested_time')
    )

    today = date.today()
    _, days_in_month = calendar.monthrange(year, month)
    available_days = []

    for day in range(1, days_in_month + 1):
        d = date(year, month, day)
        if d <= today:
            continue
        if d.weekday() not in active_weekdays:
            continue
        # Check at least one slot remains for this day
        day_slots = TimeSlot.objects.filter(is_active=True, day_of_week=d.weekday())
        slot_times = _generate_slot_times(day_slots)
        remaining = [t for t in slot_times if (d, t) not in confirmed]
        if remaining:
            available_days.append(d.isoformat())

    return JsonResponse({'available_days': available_days})


@require_GET
def available_slots_view(request):
    """Return available 30-min time slots for a given date."""
    date_str = request.GET.get('date', '')
    try:
        requested = date.fromisoformat(date_str)
    except (ValueError, AttributeError):
        return JsonResponse({'error': 'Invalid date. Use YYYY-MM-DD.'}, status=400)

    if requested <= date.today():
        return JsonResponse({'slots': []})

    day_slots = TimeSlot.objects.filter(is_active=True, day_of_week=requested.weekday())
    all_times = _generate_slot_times(day_slots)

    confirmed_times = set(
        BookingRequest.objects.filter(
            requested_date=requested,
            status='confirmed',
        ).values_list('requested_time', flat=True)
    )

    slots = [
        {
            'value': t.strftime('%H:%M'),
            'label': _format_time(requested, t),
        }
        for t in all_times
        if t not in confirmed_times
    ]

    return JsonResponse({'slots': slots})


def _format_date(d):
    return d.strftime('%A, %B ') + str(d.day) + d.strftime(', %Y')


def _format_time(d, t):
    dt = datetime.combine(d, t)
    return dt.strftime('%I:%M %p').lstrip('0') or '12:00 AM'


def _send_booking_emails(booking):
    """Send visitor acknowledgement + admin notification emails."""
    date_str = _format_date(booking.requested_date)
    time_str = _format_time(booking.requested_date, booking.requested_time)
    context = {'booking': booking, 'date_str': date_str, 'time_str': time_str}

    # Visitor acknowledgement
    try:
        visitor_html = render_to_string('emails/booking_visitor_received.html', context)
        send_mail(
            subject='Your Discovery Call Request — Zimplixio',
            message=strip_tags(visitor_html),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.email],
            html_message=visitor_html,
            fail_silently=True,
        )
    except Exception:
        logger.exception('Failed to send visitor booking acknowledgement email')

    # Admin notification
    admin_email = getattr(settings, 'LEAD_NOTIFICATION_EMAIL', '')
    if admin_email:
        try:
            admin_html = render_to_string('emails/booking_admin_notification.html', context)
            send_mail(
                subject=f'New Booking: {booking.name} — {date_str} {time_str}',
                message=strip_tags(admin_html),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[admin_email],
                html_message=admin_html,
                fail_silently=True,
            )
        except Exception:
            logger.exception('Failed to send admin booking notification email')


class BookCallView(CreateView):
    template_name = 'booking/book.html'
    form_class = BookingForm
    success_url = reverse_lazy('booking:booking_success')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['available_times'] = []
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        _send_booking_emails(self.object)
        return response

    @method_decorator(ratelimit(key='ip', rate='5/h', method='POST', block=False))
    def post(self, request, *args, **kwargs):
        if getattr(request, 'limited', False):
            return HttpResponse('Too many submissions. Please try again later.', status=429)
        return super().post(request, *args, **kwargs)


class BookingSuccessView(TemplateView):
    template_name = 'booking/booking_success.html'
