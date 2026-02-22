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
