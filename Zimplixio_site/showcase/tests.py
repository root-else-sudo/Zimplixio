from django.test import TestCase
from django.urls import reverse
from .models import TechTag, ShowcaseProject


class ShowcaseTestMixin:
    @classmethod
    def setUpTestData(cls):
        cls.tag = TechTag.objects.create(name='Python')
        cls.published = ShowcaseProject.objects.create(
            title='Published Project',
            slug='published-project',
            summary='A published test project.',
            business_problem='Problem text.',
            approach='Approach text.',
            solution_description='Solution text.',
            outcomes='Outcome text.',
            industry='healthcare',
            is_published=True,
            order=1,
        )
        cls.published.tech_tags.add(cls.tag)
        cls.unpublished = ShowcaseProject.objects.create(
            title='Unpublished Project',
            slug='unpublished-project',
            summary='An unpublished test project.',
            business_problem='Problem text.',
            approach='Approach text.',
            solution_description='Solution text.',
            outcomes='Outcome text.',
            industry='automotive',
            is_published=False,
            order=2,
        )
        cls.demo_project = ShowcaseProject.objects.create(
            title='Demo Project',
            slug='demo-project',
            summary='A project with interactive demo.',
            business_problem='Problem text.',
            approach='Approach text.',
            solution_description='Solution text.',
            outcomes='Outcome text.',
            industry='ecommerce',
            is_published=True,
            order=3,
            live_demo_url='https://recomares.com',
            system_design_url='https://recomares.com/system-design',
        )


class ShowcaseGalleryTests(ShowcaseTestMixin, TestCase):
    def test_gallery_page(self):
        response = self.client.get(reverse('showcase:gallery'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Published Project')
        self.assertNotContains(response, 'Unpublished Project')

    def test_gallery_filter_by_industry(self):
        response = self.client.get(reverse('showcase:gallery') + '?industry=healthcare')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Published Project')

    def test_gallery_filter_empty(self):
        response = self.client.get(reverse('showcase:gallery') + '?industry=ecommerce')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Published Project')


class ShowcaseDetailTests(ShowcaseTestMixin, TestCase):
    def test_detail_published(self):
        response = self.client.get(reverse('showcase:detail', kwargs={'slug': 'published-project'}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Published Project')

    def test_detail_unpublished_404(self):
        response = self.client.get(reverse('showcase:detail', kwargs={'slug': 'unpublished-project'}))
        self.assertEqual(response.status_code, 404)

    def test_detail_nonexistent_404(self):
        response = self.client.get(reverse('showcase:detail', kwargs={'slug': 'does-not-exist'}))
        self.assertEqual(response.status_code, 404)


class ShowcaseModelFieldTests(ShowcaseTestMixin, TestCase):
    def test_demo_fields_default_blank(self):
        self.assertEqual(self.published.live_demo_url, '')
        self.assertEqual(self.published.system_design_url, '')

    def test_demo_fields_store_urls(self):
        self.assertEqual(self.demo_project.live_demo_url, 'https://recomares.com')
        self.assertEqual(self.demo_project.system_design_url, 'https://recomares.com/system-design')

    def test_demo_fields_round_trip(self):
        self.demo_project.refresh_from_db()
        self.assertEqual(self.demo_project.live_demo_url, 'https://recomares.com')
        self.assertEqual(self.demo_project.system_design_url, 'https://recomares.com/system-design')


class ShowcaseDetailDemoTests(ShowcaseTestMixin, TestCase):
    def test_iframe_renders_when_url_set(self):
        response = self.client.get(reverse('showcase:detail', kwargs={'slug': 'demo-project'}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="demo-iframe"')
        self.assertContains(response, 'https://recomares.com')

    def test_iframe_hidden_when_no_url(self):
        response = self.client.get(reverse('showcase:detail', kwargs={'slug': 'published-project'}))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'id="demo-iframe"')

    def test_system_design_toggle_renders(self):
        response = self.client.get(reverse('showcase:detail', kwargs={'slug': 'demo-project'}))
        self.assertContains(response, 'System Design')
        self.assertContains(response, 'https://recomares.com/system-design')

    def test_system_design_toggle_hidden_when_no_url(self):
        self.demo_project.system_design_url = ''
        self.demo_project.save()
        response = self.client.get(reverse('showcase:detail', kwargs={'slug': 'demo-project'}))
        self.assertNotContains(response, 'System Design')
        # Restore for other tests
        self.demo_project.system_design_url = 'https://recomares.com/system-design'
        self.demo_project.save()

    def test_fallback_link_present(self):
        response = self.client.get(reverse('showcase:detail', kwargs={'slug': 'demo-project'}))
        self.assertContains(response, 'Open in a new tab')


class ShowcaseGalleryDemoBadgeTests(ShowcaseTestMixin, TestCase):
    def test_badge_shows_for_demo_project(self):
        response = self.client.get(reverse('showcase:gallery'))
        self.assertContains(response, 'Live Demo')

    def test_badge_hidden_for_project_without_demo(self):
        response = self.client.get(reverse('showcase:gallery') + '?industry=healthcare')
        self.assertNotContains(response, 'Live Demo')
