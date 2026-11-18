import json
import time as time_module
from contextlib import contextmanager
from datetime import date, datetime, time
from unittest.mock import patch
from zoneinfo import ZoneInfo

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from django.core import mail
from django.core.cache import cache

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
        from .forms import make_form_token
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'company': 'Test Co',
            'requested_date': '2026-03-15',
            'requested_time': '09:00',
            'message': 'Looking forward to the call.',
            'website': '',
            'ts': make_form_token(issued_at=time_module.time() - 30),
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


class AdminTimestampDisplayTests(TestCase):
    """Admin timestamps must render in the business timezone, not UTC.

    Guards a project-wide setting (`TIME_ZONE`), tested here because this is
    where it bites hardest: the booking changelist shows `created_at` beside
    `requested_date`/`requested_time`. The latter are naive fields holding
    Eastern values, so with TIME_ZONE='UTC' a single row displayed two
    timezones five hours apart with nothing marking which was which.
    """

    # 18:28 UTC on 17 Nov 2026 is 13:28 Eastern.
    CREATED_UTC = datetime(2026, 11, 17, 18, 28, tzinfo=ZoneInfo('UTC'))

    @classmethod
    def setUpTestData(cls):
        get_user_model().objects.create_superuser(
            username='admin', email='a@example.com', password='pw-for-tests-only')
        b = BookingRequest.objects.create(
            name='Timestamp Probe', email='probe@example.com',
            requested_date=date(2026, 11, 18), requested_time=time(10, 30),
            visitor_timezone='America/New_York', status='pending')
        BookingRequest.objects.filter(pk=b.pk).update(created_at=cls.CREATED_UTC)

    def setUp(self):
        self.client.login(username='admin', password='pw-for-tests-only')

    def test_changelist_shows_eastern_not_utc(self):
        html = self.client.get(
            reverse('admin:booking_bookingrequest_changelist')).content.decode()
        self.assertIn('1:28 p.m.', html,
                      'created_at should render as 13:28 Eastern')
        self.assertNotIn('6:28 p.m.', html,
                         'created_at is still rendering as 18:28 UTC')

    def test_requested_time_is_unchanged(self):
        """The naive TimeField must not be shifted by the display timezone."""
        html = self.client.get(
            reverse('admin:booking_bookingrequest_changelist')).content.decode()
        self.assertIn('10:30 a.m.', html)


class BookingAntiSpamTests(TestCase):
    """The booking form mails whatever address it is handed, twice.

    `/book/` is linked from the header of every page and had no bot defence
    at all -- which is precisely the shape of the contact form before the
    November 2026 campaign got the sending mailbox restricted. Same two
    signals, same asymmetry: refuse the conclusive one, store the rest.
    """

    BASE = {
        'name': 'Ada Lovelace',
        'email': 'ada@example.com',
        'company': 'Analytical Engines',
        'requested_date': '2026-12-02',
        'requested_time': '10:00',
        'visitor_timezone': 'America/New_York',
        'message': 'Looking forward to it.',
    }

    @classmethod
    def setUpTestData(cls):
        TimeSlot.objects.create(day_of_week=2, start_time=time(10, 0),
                                end_time=time(16, 0), is_active=True)

    def setUp(self):
        cache.clear()
        mail.outbox = []

    def payload(self, *, age_seconds=30, honeypot='', token=None, **over):
        from .forms import make_form_token
        data = dict(self.BASE)
        data['website'] = honeypot
        data['ts'] = token if token is not None else make_form_token(
            issued_at=time_module.time() - age_seconds)
        data.update(over)
        return data

    # ---------- a genuine booking still works ----------
    def test_human_booking_is_clean_and_sends_both_emails(self):
        r = self.client.post(reverse('booking:book'), self.payload())
        self.assertEqual(r.status_code, 302)
        b = BookingRequest.objects.get()
        self.assertFalse(b.is_spam)
        self.assertEqual(len(mail.outbox), 2, 'visitor acknowledgement + admin notice')

    # ---------- the conclusive signal is refused outright ----------
    def test_sub_three_second_booking_is_refused_and_stores_nothing(self):
        r = self.client.post(reverse('booking:book'), self.payload(age_seconds=0.5))
        self.assertEqual(r.status_code, 200)
        self.assertFalse(BookingRequest.objects.exists())
        self.assertEqual(len(mail.outbox), 0)

    # ---------- recoverable signals are stored, never mailed ----------
    def test_honeypot_booking_is_stored_but_never_emailed(self):
        r = self.client.post(reverse('booking:book'),
                             self.payload(honeypot='http://spam.example'))
        self.assertEqual(r.status_code, 302, 'a bot must still see the success redirect')
        b = BookingRequest.objects.get()
        self.assertTrue(b.is_spam)
        self.assertEqual(b.spam_reason, 'honeypot')
        self.assertEqual(len(mail.outbox), 0,
                         'no mail may leave for a flagged booking')

    def test_missing_token_is_stored_but_never_emailed(self):
        self.client.post(reverse('booking:book'), self.payload(token=''))
        b = BookingRequest.objects.get()
        self.assertTrue(b.is_spam)
        self.assertEqual(b.spam_reason, 'no_token')
        self.assertEqual(len(mail.outbox), 0)

    def test_raw_post_with_no_antispam_fields_is_flagged(self):
        """What a bot that never fetched the page would send."""
        self.client.post(reverse('booking:book'), dict(self.BASE))
        self.assertTrue(BookingRequest.objects.get().is_spam)
        self.assertEqual(len(mail.outbox), 0)

    # ---------- the decoy must be invisible ----------
    def test_decoy_is_hidden_inline_not_via_stylesheet(self):
        html = self.client.get(reverse('booking:book')).content.decode()
        self.assertIn('name="website"', html)
        row = [l for l in html.splitlines() if 'name="website"' in l][0]
        self.assertIn('display:none', row.replace(' ', ''))
        self.assertIn('tabindex="-1"', row)
        self.assertIn('aria-hidden="true"', row)
