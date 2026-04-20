import calendar
import logging
from datetime import date

from django.http import HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_GET
from django.views.generic import TemplateView, CreateView
from django_ratelimit.decorators import ratelimit

from .forms import BookingForm
from .models import BookingRequest, TimeSlot
from .services import BookingEmailService

logger = logging.getLogger(__name__)


@require_GET
def available_days_view(request):
    """Return which calendar days in a given month have available slots."""
    month_str = request.GET.get('month', '')
    try:
        year, month = [int(x) for x in month_str.split('-')]
        date(year, month, 1)
    except (ValueError, AttributeError):
        return JsonResponse({'error': 'Invalid month. Use YYYY-MM.'}, status=400)

    active_weekdays = set(
        TimeSlot.objects.filter(is_active=True).values_list('day_of_week', flat=True)
    )
    confirmed = BookingRequest.objects.confirmed_slots_for_month(year, month)

    today = date.today()
    _, days_in_month = calendar.monthrange(year, month)
    available_days = []

    for day in range(1, days_in_month + 1):
        d = date(year, month, day)
        if d <= today:
            continue
        if d.weekday() not in active_weekdays:
            continue
        day_slots = TimeSlot.objects.filter(is_active=True, day_of_week=d.weekday())
        slot_times = day_slots.generate_times()
        if any((d, t) not in confirmed for t in slot_times):
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
    all_times = day_slots.generate_times()
    confirmed_times = BookingRequest.objects.confirmed_times_for_date(requested)

    from .utils import format_time
    slots = [
        {
            'value': t.strftime('%H:%M'),
            'label': format_time(requested, t),
        }
        for t in all_times
        if t not in confirmed_times
    ]

    return JsonResponse({'slots': slots})


class BookCallView(CreateView):
    template_name = 'booking/book.html'
    form_class = BookingForm
    success_url = reverse_lazy('booking:booking_success')

    def form_valid(self, form):
        response = super().form_valid(form)
        BookingEmailService.send_visitor_received(self.object)
        BookingEmailService.send_admin_notification(self.object)
        return response

    @method_decorator(ratelimit(key='ip', rate='5/h', method='POST', block=False))
    def post(self, request, *args, **kwargs):
        if getattr(request, 'limited', False):
            return HttpResponse('Too many submissions. Please try again later.', status=429)
        return super().post(request, *args, **kwargs)


class BookingSuccessView(TemplateView):
    template_name = 'booking/booking_success.html'
