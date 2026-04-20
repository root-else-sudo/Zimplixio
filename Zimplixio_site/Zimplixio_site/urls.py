from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.generic import TemplateView

from core.sitemaps import StaticViewSitemap, ShowcaseSitemap

admin.site.site_header = 'Zimplixio Administration'
admin.site.site_title = 'Zimplixio Admin'
admin.site.index_title = 'Site Management'

sitemaps = {
    'static': StaticViewSitemap,
    'showcase': ShowcaseSitemap,
}

urlpatterns = [
    path('zm-admin/', admin.site.urls),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    path('showcase/', include('showcase.urls')),
    path('results/', include('metrics.urls')),
    path('book/', include('booking.urls')),
    path('framework/', include('framework.urls')),
    path('', include('pages.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
