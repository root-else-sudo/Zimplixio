from datetime import time
from django.test import TestCase
from django.urls import reverse
from .models import TimeSlot, BookingRequest


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


class AvailableSlotsTests(TestCase):
    def test_available_times_generated(self):
        TimeSlot.objects.create(day_of_week=0, start_time=time(9, 0), end_time=time(10, 0), is_active=True)
        from booking.views import get_available_times
        times = get_available_times()
        self.assertEqual(len(times), 2)  # 9:00 and 9:30
        self.assertEqual(times[0], time(9, 0))
        self.assertEqual(times[1], time(9, 30))
