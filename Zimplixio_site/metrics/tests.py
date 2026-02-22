from datetime import date
from django.test import TestCase
from django.urls import reverse
from .models import NPSMetric


class NPSResultsTests(TestCase):
    def test_results_page_no_data(self):
        response = self.client.get(reverse('metrics:results'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'NPS data will be published')

    def test_results_page_with_data(self):
        NPSMetric.objects.create(score=72, total_responses=50, last_updated=date(2026, 1, 15), is_active=True)
        response = self.client.get(reverse('metrics:results'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '72')
        self.assertContains(response, '50')


class NPSSingleActiveTests(TestCase):
    def test_single_active_enforcement(self):
        m1 = NPSMetric.objects.create(score=60, total_responses=30, last_updated=date(2025, 12, 1), is_active=True)
        m2 = NPSMetric.objects.create(score=75, total_responses=50, last_updated=date(2026, 1, 15), is_active=True)
        m1.refresh_from_db()
        self.assertFalse(m1.is_active)
        self.assertTrue(m2.is_active)


class NPSContextProcessorTests(TestCase):
    def test_nps_in_context(self):
        NPSMetric.objects.create(score=80, total_responses=100, last_updated=date(2026, 2, 1), is_active=True)
        response = self.client.get(reverse('pages:home'))
        self.assertEqual(response.context['nps_score'], 80)
        self.assertEqual(response.context['nps_total_responses'], 100)

    def test_no_nps_graceful(self):
        response = self.client.get(reverse('pages:home'))
        self.assertNotIn('nps_score', response.context)
