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
