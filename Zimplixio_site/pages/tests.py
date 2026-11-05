from unittest.mock import patch

from django.conf import settings
from django.core import mail
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
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
    VALID = {
        'name': 'Ada Lovelace',
        'email': 'ada@example.com',
        'company': 'Analytical Engines',
        'message': 'We need help forecasting demand.',
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
