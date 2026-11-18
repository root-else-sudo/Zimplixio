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


class CalendarInviteTests(TestCase):
    """The confirmation email carries a real iCalendar invitation.

    The trap this suite exists for is the timezone one: `requested_date` and
    `requested_time` are naive values that *mean* Eastern, and DTSTART has to
    go out as a UTC instant. Combining them without attaching Eastern first
    is the same mistake that hid a whole day of availability every evening --
    here it would silently put every invite five hours off.
    """

    def _booking(self, **over):
        data = dict(
            name='Ada Lovelace',
            email='ada@example.com',
            company='Analytical Engines',
            requested_date=date(2026, 11, 19),
            requested_time=time(15, 30),
            visitor_timezone='America/New_York',
            message='Looking forward to it.',
        )
        data.update(over)
        return BookingRequest.objects.create(**data)

    # ---------- the timezone conversion ----------
    def test_dtstart_is_the_eastern_slot_expressed_in_utc(self):
        from .calendar_invite import build_invite
        ics = build_invite(self._booking())
        # 15:30 EST (UTC-5) on 2026-11-19 is 20:30 UTC.
        self.assertIn('DTSTART:20261119T203000Z', ics)

    def test_dtstart_respects_daylight_saving(self):
        """A hardcoded -5 offset passes the EST test and fails this one."""
        from .calendar_invite import build_invite
        ics = build_invite(self._booking(requested_date=date(2026, 7, 15)))
        # 15:30 EDT (UTC-4) on 2026-07-15 is 19:30 UTC.
        self.assertIn('DTSTART:20260715T193000Z', ics)

    def test_dtend_is_one_slot_after_dtstart(self):
        from django.conf import settings
        from .calendar_invite import build_invite
        self.assertEqual(getattr(settings, 'BOOKING_DURATION_MINUTES', None), 30)
        ics = build_invite(self._booking())
        self.assertIn('DTEND:20261119T210000Z', ics)

    # ---------- identity of the event ----------
    def test_uid_is_stable_and_tied_to_the_booking(self):
        from .calendar_invite import build_invite
        booking = self._booking()
        expected = 'UID:booking-%s@zimplixio.com' % booking.pk
        self.assertIn(expected, build_invite(booking))
        # Same booking, built again -> same UID, so clients update rather
        # than creating a second event.
        self.assertIn(expected, build_invite(booking))

    def test_organizer_is_the_sending_address_not_the_admin(self):
        from django.conf import settings
        from .calendar_invite import build_invite
        ics = build_invite(self._booking())
        self.assertIn('mailto:%s' % settings.DEFAULT_FROM_EMAIL, ics)

    def test_visitor_is_an_attendee_who_is_asked_to_rsvp(self):
        from .calendar_invite import build_invite
        # Unfold first: the spec wraps at 75 octets, mid-parameter if need be.
        ics = build_invite(self._booking()).replace('\r\n ', '')
        self.assertIn('RSVP=TRUE', ics)
        self.assertIn('mailto:ada@example.com', ics)

    # ---------- request vs cancel ----------
    def test_confirmation_invite_is_a_request(self):
        from .calendar_invite import build_invite
        ics = build_invite(self._booking())
        self.assertIn('METHOD:REQUEST', ics)
        self.assertIn('STATUS:CONFIRMED', ics)
        self.assertIn('SEQUENCE:0', ics)

    def test_cancellation_retracts_the_event(self):
        """Without this the meeting stays on the visitor's calendar forever."""
        from .calendar_invite import build_invite
        ics = build_invite(self._booking(), method='CANCEL')
        self.assertIn('METHOD:CANCEL', ics)
        self.assertIn('STATUS:CANCELLED', ics)
        # A cancellation must outrank the request it supersedes.
        self.assertIn('SEQUENCE:1', ics)

    # ---------- RFC 5545 mechanics ----------
    def test_lines_are_crlf_terminated(self):
        from .calendar_invite import build_invite
        ics = build_invite(self._booking())
        self.assertTrue(ics.startswith('BEGIN:VCALENDAR\r\n'))
        self.assertTrue(ics.rstrip('\r\n').endswith('END:VCALENDAR'))
        self.assertNotIn('\n\n', ics.replace('\r\n', '\n'))

    def test_long_lines_are_folded_to_75_octets(self):
        from .calendar_invite import build_invite
        with self.settings(ZOOM_MEETING_URL='https://us05web.zoom.us/j/9648777904'
                                            '?pwd=wYxDbqBSJWgav9aC3KsbjAJwLM9ZEv.1'):
            ics = build_invite(self._booking())
        for line in ics.split('\r\n'):
            self.assertLessEqual(len(line.encode('utf-8')), 75, repr(line))

    def test_text_values_are_escaped(self):
        """An unescaped comma or newline silently truncates the field."""
        from .calendar_invite import build_invite
        ics = build_invite(self._booking(
            name='Lovelace, Ada', message='Line one\nLine two; with a semicolon'))
        unfolded = ics.replace('\r\n ', '')
        self.assertIn('Lovelace\\, Ada', unfolded)
        self.assertIn('\\n', unfolded)
        self.assertIn('\\;', unfolded)

    def test_admin_is_an_attendee_too(self):
        """The event should name both parties, not just the visitor."""
        from .calendar_invite import build_invite
        with self.settings(LEAD_NOTIFICATION_EMAIL='joe@zimplixio.com'):
            ics = build_invite(self._booking())
        self.assertIn('mailto:joe@zimplixio.com', ics.replace('\r\n ', ''))

    def test_host_and_organizer_have_distinct_names(self):
        """Both carried CN=Zimplixio, so a guest list read 'Zimplixio, Zimplixio'."""
        from django.conf import settings
        from .calendar_invite import build_invite
        self.assertEqual(getattr(settings, 'BOOKING_HOST_NAME', None), 'Joe Ugalde')
        with self.settings(LEAD_NOTIFICATION_EMAIL='joe@zimplixio.com'):
            unfolded = build_invite(self._booking()).replace('\r\n ', '')
        host_line = [l for l in unfolded.split('\r\n')
                     if l.startswith('ATTENDEE') and 'joe@zimplixio.com' in l][0]
        self.assertIn('CN="Joe Ugalde"', host_line)
        organizer = [l for l in unfolded.split('\r\n') if l.startswith('ORGANIZER')][0]
        self.assertIn('CN="Zimplixio"', organizer)

    # ---------- the title ----------
    def test_title_names_the_visitor(self):
        """A generic title tells neither side who the call is with."""
        from .calendar_invite import build_invite
        unfolded = build_invite(self._booking()).replace('\r\n ', '')
        summary = [l for l in unfolded.split('\r\n') if l.startswith('SUMMARY')][0]
        self.assertIn('Ada Lovelace', summary)
        self.assertIn('Zimplixio', summary)

    def test_title_survives_a_name_with_a_comma(self):
        from .calendar_invite import build_invite
        unfolded = build_invite(
            self._booking(name='Lovelace, Ada')).replace('\r\n ', '')
        summary = [l for l in unfolded.split('\r\n') if l.startswith('SUMMARY')][0]
        self.assertIn('Lovelace\\, Ada', summary)

    def test_title_falls_back_when_the_name_is_blank(self):
        """Never ship a title with a dangling separator and no name."""
        from .calendar_invite import build_invite
        unfolded = build_invite(self._booking(name='')).replace('\r\n ', '')
        summary = [l for l in unfolded.split('\r\n') if l.startswith('SUMMARY')][0]
        self.assertEqual(summary, 'SUMMARY:Discovery Call - Zimplixio')

    def test_visitor_attendee_carries_their_registered_name(self):
        """It is what the host's calendar shows as the guest."""
        from .calendar_invite import build_invite
        unfolded = build_invite(self._booking()).replace('\r\n ', '')
        visitor = [l for l in unfolded.split('\r\n')
                   if l.startswith('ATTENDEE') and 'ada@example.com' in l][0]
        self.assertIn('CN="Ada Lovelace"', visitor)

    def test_zoom_url_is_carried_into_the_event(self):
        from .calendar_invite import build_invite
        with self.settings(ZOOM_MEETING_URL='https://example.zoom.us/j/123'):
            ics = build_invite(self._booking())
        self.assertIn('https://example.zoom.us/j/123', ics.replace('\r\n ', ''))


class CalendarInviteDeliveryTests(TestCase):
    """The invite has to actually leave the building, attached correctly."""

    def setUp(self):
        mail.outbox = []
        self.booking = BookingRequest.objects.create(
            name='Ada Lovelace', email='ada@example.com',
            requested_date=date(2026, 11, 19), requested_time=time(15, 30),
            visitor_timezone='America/New_York')

    def _ics_parts(self, message):
        return [a for a in message.attachments
                if 'text/calendar' in str(a)] or [
            a for a in getattr(message, 'alternatives', [])
            if 'text/calendar' in str(a[1])]

    def test_confirmation_email_attaches_the_invite(self):
        self.booking.confirm()
        msg = mail.outbox[-1]
        self.assertTrue(self._ics_parts(msg), 'no text/calendar part on the confirmation')
        self.assertIn('METHOD:REQUEST', str(msg.message()))

    def test_confirmation_still_has_its_html_body(self):
        """Attaching must not cost us the styled email."""
        self.booking.confirm()
        body = str(mail.outbox[-1].message())
        self.assertIn('text/html', body)
        self.assertIn('Join Zoom Meeting', body.replace('=\n', ''))

    def test_cancellation_email_retracts_the_invite(self):
        self.booking.confirm()
        mail.outbox = []
        self.booking.cancel()
        msg = mail.outbox[-1]
        self.assertTrue(self._ics_parts(msg), 'no text/calendar part on the cancellation')
        self.assertIn('METHOD:CANCEL', str(msg.message()))

    def test_confirmation_copies_the_admin_so_both_calendars_get_it(self):
        with self.settings(LEAD_NOTIFICATION_EMAIL='joe@zimplixio.com'):
            self.booking.confirm()
        self.assertIn('joe@zimplixio.com', mail.outbox[-1].cc)

    def test_admin_notification_is_not_an_invite(self):
        """The admin mail fires on request, before the slot is accepted."""
        from .services import BookingEmailService
        with self.settings(LEAD_NOTIFICATION_EMAIL='joe@zimplixio.com'):
            BookingEmailService.send_admin_notification(self.booking)
        self.assertNotIn('METHOD:REQUEST', str(mail.outbox[-1].message()))
