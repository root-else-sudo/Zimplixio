import time
from io import StringIO
from unittest.mock import patch

from django.conf import settings
from django.core import mail
from django.core.cache import cache
from django.core.management import call_command
from django.contrib.admin.sites import AdminSite
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from .admin import ContactSubmissionAdmin
from .models import ContactSubmission


class PageStatusTests(TestCase):
    def test_home_page(self):
        response = self.client.get(reverse('pages:home'))
        self.assertEqual(response.status_code, 200)

    def test_about_page(self):
        response = self.client.get(reverse('pages:about'))
        self.assertEqual(response.status_code, 200)

    def test_contact_page(self):
        response = self.client.get(reverse('pages:contact'))
        self.assertEqual(response.status_code, 200)

    def test_contact_success_page(self):
        response = self.client.get(reverse('pages:contact_success'))
        self.assertEqual(response.status_code, 200)

    def test_privacy_policy_page(self):
        response = self.client.get(reverse('pages:privacy_policy'))
        self.assertEqual(response.status_code, 200)

    def test_cookie_policy_page(self):
        response = self.client.get(reverse('pages:cookie_policy'))
        self.assertEqual(response.status_code, 200)


class ContactFormTests(TestCase):
    def test_contact_form_submit(self):
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'company': 'Test Co',
            'message': 'Hello, this is a test message.',
        }
        response = self.client.post(reverse('pages:contact'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ContactSubmission.objects.filter(email='test@example.com').exists())

    def test_contact_form_validation(self):
        data = {
            'name': '',
            'email': 'invalid',
            'message': '',
        }
        response = self.client.post(reverse('pages:contact'), data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(ContactSubmission.objects.exists())


class ContactConfirmationEmailTests(TestCase):
    @property
    def VALID(self):
        """A submission as a real browser sends it — decoy empty, token stamped.

        A property rather than a class attribute so every access gets a fresh
        token; a stale one would be rejected by the dwell-time check.
        """
        from pages.forms import make_form_token
        return {
            'name': 'Ada Lovelace',
            'email': 'ada@example.com',
            'company': 'Analytical Engines',
            'message': 'We need help forecasting demand.',
            'website': '',
            'ts': make_form_token(issued_at=time.time() - 30),
        }

    def setUp(self):
        # django-ratelimit counts in the default LocMemCache, which Django does
        # not reset between test methods — without this the 5/h cap leaks across
        # tests and later POSTs get a 429 instead of exercising the view.
        cache.clear()

    def test_confirmation_email_sent_to_visitor(self):
        self.client.post(reverse('pages:contact'), self.VALID)
        self.assertEqual(len(mail.outbox), 1)
        sent = mail.outbox[0]
        self.assertEqual(sent.to, ['ada@example.com'])
        self.assertEqual(sent.subject, "We've received your message — Zimplixio")
        self.assertEqual(sent.from_email, settings.DEFAULT_FROM_EMAIL)

    def test_confirmation_email_includes_their_name_and_message(self):
        self.client.post(reverse('pages:contact'), self.VALID)
        sent = mail.outbox[0]
        html = sent.alternatives[0][0]
        self.assertIn('Ada Lovelace', html)
        self.assertIn('We need help forecasting demand.', html)
        self.assertIn('Ada Lovelace', sent.body)

    def test_html_alternative_is_attached(self):
        self.client.post(reverse('pages:contact'), self.VALID)
        sent = mail.outbox[0]
        self.assertEqual(len(sent.alternatives), 1)
        self.assertEqual(sent.alternatives[0][1], 'text/html')

    def test_message_is_escaped_in_email(self):
        data = dict(self.VALID, message='<script>alert(1)</script>')
        self.client.post(reverse('pages:contact'), data)
        html = mail.outbox[0].alternatives[0][0]
        self.assertNotIn('<script>alert(1)</script>', html)
        self.assertIn('&lt;script&gt;', html)

    def test_no_email_when_submission_is_invalid(self):
        self.client.post(reverse('pages:contact'), {'name': '', 'email': 'bad', 'message': ''})
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(ContactSubmission.objects.count(), 0)

    def test_submission_survives_email_failure(self):
        with patch('pages.services.send_mail', side_effect=Exception('smtp down')):
            response = self.client.post(reverse('pages:contact'), self.VALID)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ContactSubmission.objects.count(), 1)

    def test_plaintext_fallback_is_clean(self):
        data = dict(self.VALID, message='First paragraph.\n\nSecond paragraph.')
        self.client.post(reverse('pages:contact'), data)
        body = mail.outbox[0].body
        self.assertNotIn('margin: 0', body, 'CSS leaked into the plain-text body')
        self.assertNotIn('font-family', body)
        self.assertNotIn('&mdash;', body, 'HTML entities left undecoded')
        self.assertNotIn('&#x27;', body)
        self.assertNotIn('&amp;', body)
        self.assertIn('First paragraph.', body)
        self.assertIn('Second paragraph.', body)
        self.assertNotIn('First paragraph.Second', body, 'line breaks were lost')


class ContactSpamFilterTests(TestCase):
    """Honeypot + dwell-time gating, and the email suppression that depends on it."""

    BASE = {
        'name': 'Ada Lovelace',
        'email': 'ada@example.com',
        'company': 'Analytical Engines',
        'message': 'We need help forecasting demand.',
    }

    def setUp(self):
        cache.clear()
        mail.outbox = []

    def payload(self, *, age_seconds=30, honeypot='', token=None, **overrides):
        """A submission as a real browser would send it."""
        from pages.forms import make_form_token
        data = dict(self.BASE)
        data['website'] = honeypot
        data['ts'] = token if token is not None else make_form_token(
            issued_at=time.time() - age_seconds
        )
        data.update(overrides)
        return data

    # ---------- a genuine submission still works ----------
    def test_human_submission_is_clean_and_emailed(self):
        r = self.client.post(reverse('pages:contact'), self.payload())
        self.assertEqual(r.status_code, 302)
        s = ContactSubmission.objects.get()
        self.assertFalse(s.is_spam)
        self.assertEqual(len(mail.outbox), 1)

    # ---------- honeypot ----------
    def test_honeypot_filled_is_flagged_and_not_emailed(self):
        r = self.client.post(reverse('pages:contact'),
                             self.payload(honeypot='http://spam.example'))
        self.assertEqual(r.status_code, 302, 'bot must still see the success redirect')
        s = ContactSubmission.objects.get()
        self.assertTrue(s.is_spam)
        self.assertEqual(len(mail.outbox), 0, 'no mail may leave for a flagged submission')

    # ---------- dwell time ----------
    def test_submitted_too_fast_is_flagged(self):
        self.client.post(reverse('pages:contact'), self.payload(age_seconds=0.5))
        self.assertTrue(ContactSubmission.objects.get().is_spam)
        self.assertEqual(len(mail.outbox), 0)

    def test_slow_genuine_submission_is_clean(self):
        self.client.post(reverse('pages:contact'), self.payload(age_seconds=1800))
        self.assertFalse(ContactSubmission.objects.get().is_spam)
        self.assertEqual(len(mail.outbox), 1)

    def test_stale_token_is_flagged(self):
        self.client.post(reverse('pages:contact'), self.payload(age_seconds=60 * 60 * 30))
        self.assertTrue(ContactSubmission.objects.get().is_spam)
        self.assertEqual(len(mail.outbox), 0)

    # ---------- tampering / direct POSTs ----------
    def test_missing_token_is_flagged(self):
        self.client.post(reverse('pages:contact'), self.payload(token=''))
        self.assertTrue(ContactSubmission.objects.get().is_spam)
        self.assertEqual(len(mail.outbox), 0)

    def test_forged_token_is_flagged(self):
        self.client.post(reverse('pages:contact'), self.payload(token='1763000000:forged'))
        self.assertTrue(ContactSubmission.objects.get().is_spam)
        self.assertEqual(len(mail.outbox), 0)

    def test_raw_post_with_no_spam_fields_at_all_is_flagged(self):
        """What every bot in the log actually does: POST the visible fields only."""
        self.client.post(reverse('pages:contact'), dict(self.BASE))
        self.assertTrue(ContactSubmission.objects.get().is_spam)
        self.assertEqual(len(mail.outbox), 0)

    # ---------- the decoy must be invisible and skipped by assistive tech ----------
    def test_honeypot_is_hidden_inline_not_via_stylesheet(self):
        html = self.client.get(reverse('pages:contact')).content.decode()
        self.assertIn('name="website"', html)
        row = [l for l in html.splitlines() if 'name="website"' in l][0]
        self.assertIn('display:none', row.replace(' ', ''),
                      'must be hidden by an inline style, not a CSS class')
        self.assertIn('tabindex="-1"', row)
        self.assertIn('autocomplete="off"', row)
        self.assertIn('aria-hidden="true"', row)

    def test_honeypot_has_no_visible_label(self):
        html = self.client.get(reverse('pages:contact')).content.decode()
        self.assertNotIn('>Website<', html)


class ContactAdminActionTests(TestCase):
    """Bulk actions — the admin had none, so clearing 2k rows meant one at a time."""

    def setUp(self):
        self.admin = ContactSubmissionAdmin(ContactSubmission, AdminSite())
        self.request = RequestFactory().get('/')
        self.request.user = None
        # message_user needs a message store
        setattr(self.request, 'session', {})
        setattr(self.request, '_messages', FallbackStorage(self.request))
        for i in range(3):
            ContactSubmission.objects.create(
                name=f'n{i}', email=f'u{i}@example.com', message='m')

    def test_submissions_cannot_be_added_through_admin(self):
        self.assertFalse(self.admin.has_add_permission(self.request))

    def test_mark_as_read_updates_every_selected_row(self):
        self.admin.mark_as_read(self.request, ContactSubmission.objects.all())
        self.assertEqual(ContactSubmission.objects.filter(is_read=True).count(), 3)

    def test_mark_as_unread_reverses_it(self):
        ContactSubmission.objects.update(is_read=True)
        self.admin.mark_as_unread(self.request, ContactSubmission.objects.all())
        self.assertEqual(ContactSubmission.objects.filter(is_read=False).count(), 3)

    def test_mark_as_spam_sets_flag_and_reason(self):
        self.admin.mark_as_spam(self.request, ContactSubmission.objects.all())
        self.assertEqual(ContactSubmission.objects.filter(
            is_spam=True, spam_reason='manual').count(), 3)

    def test_mark_as_not_spam_clears_flag_and_reason(self):
        ContactSubmission.objects.update(is_spam=True, spam_reason='honeypot')
        self.admin.mark_as_not_spam(self.request, ContactSubmission.objects.all())
        self.assertEqual(ContactSubmission.objects.filter(
            is_spam=False, spam_reason='').count(), 3)

    def test_spam_can_be_filtered_in_the_changelist(self):
        self.assertIn('is_spam', self.admin.list_filter)
        self.assertIn('is_spam', self.admin.list_display)


class FlagContactSpamCommandTests(TestCase):
    """One-off backfill that classifies the submissions already in the table."""

    def setUp(self):
        self.google = ContactSubmission.objects.create(
            name='Robertfus', email='a@gmail.com', company='google',
            message='Hi, I wanted to know your price.')
        self.gibberish = ContactSubmission.objects.create(
            name='empvgigkuw', email='real.person@comcast.net', company='inoyxzttod',
            message='eklnixktjnwjwsuuyhyfxhvgqxjudk')
        self.legit = ContactSubmission.objects.create(
            name='Maria Fernandez', email='maria@brightpath.com',
            company='BrightPath Logistics', message='Our dispatch scheduling is a mess.')

    def _run(self, *args):
        out = StringIO()
        call_command('flag_contact_spam', *args, stdout=out)
        return out.getvalue()

    def test_dry_run_is_the_default_and_writes_nothing(self):
        output = self._run()
        self.assertEqual(ContactSubmission.objects.filter(is_spam=True).count(), 0)
        self.assertIn('dry run', output.lower())

    def test_apply_flags_the_google_campaign(self):
        self._run('--apply')
        self.google.refresh_from_db()
        self.assertTrue(self.google.is_spam)
        self.assertEqual(self.google.spam_reason, 'company_google')

    def test_apply_flags_the_gibberish_bot(self):
        self._run('--apply')
        self.gibberish.refresh_from_db()
        self.assertTrue(self.gibberish.is_spam)
        self.assertEqual(self.gibberish.spam_reason, 'gibberish')

    def test_a_real_submission_is_left_alone(self):
        self._run('--apply')
        self.legit.refresh_from_db()
        self.assertFalse(self.legit.is_spam)
        self.assertEqual(self.legit.spam_reason, '')

    def test_rerunning_is_idempotent(self):
        self._run('--apply')
        before = list(ContactSubmission.objects.values_list('id', 'is_spam', 'spam_reason'))
        self._run('--apply')
        self.assertEqual(
            list(ContactSubmission.objects.values_list('id', 'is_spam', 'spam_reason')),
            before)

    def test_already_flagged_rows_are_not_reclassified(self):
        self.legit.is_spam = True
        self.legit.spam_reason = 'manual'
        self.legit.save()
        self._run('--apply')
        self.legit.refresh_from_db()
        self.assertEqual(self.legit.spam_reason, 'manual')
