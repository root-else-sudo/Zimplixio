from datetime import datetime, timedelta
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, CreateView
from django_ratelimit.decorators import ratelimit
from .forms import BookingForm
from .models import TimeSlot


def get_available_times():
    """Build a list of available time objects from active TimeSlots."""
    slots = TimeSlot.objects.filter(is_active=True)
    times = set()
    for slot in slots:
        current = datetime.combine(datetime.today(), slot.start_time)
        end = datetime.combine(datetime.today(), slot.end_time)
        while current < end:
            times.add(current.time())
            current += timedelta(minutes=30)
    return sorted(times)


class BookCallView(CreateView):
    template_name = 'booking/book.html'
    form_class = BookingForm
    success_url = reverse_lazy('booking:booking_success')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['available_times'] = get_available_times()
        return kwargs

    @method_decorator(ratelimit(key='ip', rate='5/h', method='POST', block=False))
    def post(self, request, *args, **kwargs):
        if getattr(request, 'limited', False):
            return HttpResponse('Too many submissions. Please try again later.', status=429)
        return super().post(request, *args, **kwargs)


class BookingSuccessView(TemplateView):
    template_name = 'booking/booking_success.html'
