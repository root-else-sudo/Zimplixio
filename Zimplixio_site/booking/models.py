from datetime import datetime, timedelta

from django.db import models


class TimeSlotQuerySet(models.QuerySet):
    def generate_times(self, interval_minutes=30):
        times = set()
        for slot in self:
            current = datetime.combine(datetime.today(), slot.start_time)
            end = datetime.combine(datetime.today(), slot.end_time)
            while current < end:
                times.add(current.time())
                current += timedelta(minutes=interval_minutes)
        return sorted(times)


class TimeSlot(models.Model):
    DAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]

    objects = TimeSlotQuerySet.as_manager()

    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        return f"{self.get_day_of_week_display()} {self.start_time:%H:%M}–{self.end_time:%H:%M}"


class BookingRequestManager(models.Manager):
    def confirmed_slots_for_month(self, year, month):
        """Return a set of (date, time) tuples for confirmed bookings in the given month."""
        return set(
            self.filter(
                requested_date__year=year,
                requested_date__month=month,
                status='confirmed',
            ).values_list('requested_date', 'requested_time')
        )

    def confirmed_times_for_date(self, date):
        """Return a set of time objects for confirmed bookings on the given date."""
        return set(
            self.filter(
                requested_date=date,
                status='confirmed',
            ).values_list('requested_time', flat=True)
        )


class BookingRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField()
    company = models.CharField(max_length=150, blank=True)
    requested_date = models.DateField()
    requested_time = models.TimeField()
    message = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    objects = BookingRequestManager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} — {self.requested_date} {self.requested_time:%H:%M} ({self.status})"

    def confirm(self):
        from .services import BookingEmailService
        self.status = 'confirmed'
        self.save()
        BookingEmailService.send_visitor_confirmed(self)
