from django.core.cache import cache

from metrics.models import NPS_CACHE_KEY, NPSMetric

_NPS_CACHE_TTL = 3600  # 1 hour


def site_context(request):
    context = {
        'site_name': 'Zimplixio',
        'site_tagline': 'Enterprise-Grade Solutions for Growing Businesses',
    }
    try:
        active = cache.get(NPS_CACHE_KEY)
        if active is None:
            active = NPSMetric.objects.filter(is_active=True).first()
            cache.set(NPS_CACHE_KEY, active, _NPS_CACHE_TTL)
        if active:
            context['nps_score'] = active.score
            context['nps_total_responses'] = active.total_responses
    except Exception:
        pass
    return context
