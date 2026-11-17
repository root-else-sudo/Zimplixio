import json
from contextlib import contextmanager
from datetime import date, datetime, time
from unittest.mock import patch
from zoneinfo import ZoneInfo

from django.test import TestCase
from django.urls import reverse

from .models import TimeSlot, BookingRequest
from .utils import today_in_booking_tz


class BookingPageTests(TestCase):
    def test_booking_page(self):
        response = self.client.get(reverse('booking:book'))
        self.assertEqual(response.status_code, 200)

    def test_booking_success_page(self):
        response = self.client.get(reverse('booking:booking_success'))
        self.assertEqual(response.status_code, 200)


class BookingFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.slot = TimeSlot.objects.create(
            day_of_week=0,
            start_time=time(9, 0),
            end_time=time(12, 0),
            is_active=True,
        )

    def test_booking_submit(self):
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'company': 'Test Co',
            'requested_date': '2026-03-15',
            'requested_time': '09:00',
            'message': 'Looking forward to the call.',
        }
        response = self.client.post(reverse('booking:book'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(BookingRequest.objects.filter(email='test@example.com').exists())

    def test_booking_validation(self):
        data = {
            'name': '',
            'email': 'invalid',
            'requested_date': '',
            'requested_time': '',
        }
        response = self.client.post(reverse('booking:book'), data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(BookingRequest.objects.exists())



class BookingDateBoundaryTests(TestCase):
    """"Today" must be computed in the booking timezone, not the server's.

    Production runs UTC with no TZ set, but availability is published in
    America/New_York. Using date.today() rolls the calendar over at 19:00
    Eastern, so from 7pm every weeknight the whole of the next day vanished
    from the calendar -- not just evening slots, every slot on that day.
    """

    # 20:00 Eastern on Tue 17 Nov 2026 == 01:00 UTC on Wed 18 Nov.
    EVENING_ET = datetime(2026, 11, 17, 20, 0, tzinfo=ZoneInfo('America/New_York'))
    TOMORROW = date(2026, 11, 18)          # Wednesday, in Eastern terms
    TODAY_ET = date(2026, 11, 17)

    @classmethod
    def setUpTestData(cls):
        TimeSlot.objects.create(day_of_week=cls.TOMORROW.weekday(),
                                start_time=time(10, 0), end_time=time(16, 0),
                                is_active=True)
        TimeSlot.objects.create(day_of_week=cls.TODAY_ET.weekday(),
                                start_time=time(10, 0), end_time=time(16, 0),
                                is_active=True)

    @contextmanager
    def _at_evening(self):
        """Simulate production: a UTC server at the moment it is 8pm Eastern.

        BOTH patches are required. `timezone.now` drives the corrected
        helper; patching `booking.views.date` reproduces what a UTC server's
        `date.today()` returns, which is what the bug actually depended on.
        Without the second patch these tests pass on a developer machine in
        Eastern while the bug is live on the server -- which is exactly what
        happened the first time they were written.
        """
        utc_now = self.EVENING_ET.astimezone(ZoneInfo('UTC'))

        class ServerDate(date):
            @classmethod
            def today(cls):
                return utc_now.date()

        with patch('django.utils.timezone.now', return_value=utc_now), \
             patch('booking.views.date', ServerDate):
            yield

    def test_today_is_resolved_in_eastern_not_utc(self):
        with self._at_evening():
            self.assertEqual(today_in_booking_tz(), self.TODAY_ET)

    def test_tomorrow_is_still_offered_at_8pm_eastern(self):
        with self._at_evening():
            r = self.client.get(reverse('booking:available_days'), {'month': '2026-11'})
        days = json.loads(r.content)['available_days']
        self.assertIn(self.TOMORROW.isoformat(), days,
                      'the next day disappears from the calendar in the evening')

    def test_tomorrows_slots_are_still_offered_at_8pm_eastern(self):
        with self._at_evening():
            r = self.client.get(reverse('booking:slots'),
                                {'date': self.TOMORROW.isoformat()})
        self.assertTrue(json.loads(r.content)['slots'],
                        'no slots returned for tomorrow')

    # ---------- the rules that must NOT change ----------
    def test_same_day_booking_is_still_refused(self):
        with self._at_evening():
            r = self.client.get(reverse('booking:slots'),
                                {'date': self.TODAY_ET.isoformat()})
            days = json.loads(self.client.get(
                reverse('booking:available_days'), {'month': '2026-11'}).content
            )['available_days']
        self.assertEqual(json.loads(r.content)['slots'], [])
        self.assertNotIn(self.TODAY_ET.isoformat(), days)

    def test_past_dates_are_still_refused(self):
        with self._at_evening():
            r = self.client.get(reverse('booking:slots'), {'date': '2026-11-10'})
        self.assertEqual(json.loads(r.content)['slots'], [])
