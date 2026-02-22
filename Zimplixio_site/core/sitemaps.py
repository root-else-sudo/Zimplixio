from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from showcase.models import ShowcaseProject


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'monthly'

    def items(self):
        return [
            'pages:home',
            'pages:about',
            'pages:contact',
            'services:services',
            'showcase:gallery',
            'metrics:results',
            'booking:book',
            'pages:privacy_policy',
            'pages:cookie_policy',
        ]

    def location(self, item):
        return reverse(item)


class ShowcaseSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.7

    def items(self):
        return ShowcaseProject.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('showcase:detail', kwargs={'slug': obj.slug})
