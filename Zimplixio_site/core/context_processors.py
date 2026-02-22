def site_context(request):
    context = {
        'site_name': 'Zimplixio',
        'site_tagline': 'Enterprise-Grade Solutions for Growing Businesses',
    }
    try:
        from metrics.models import NPSMetric
        active = NPSMetric.objects.filter(is_active=True).first()
        if active:
            context['nps_score'] = active.score
            context['nps_total_responses'] = active.total_responses
    except Exception:
        pass
    return context
