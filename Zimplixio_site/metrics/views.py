from django.views.generic import TemplateView
from .models import NPSMetric


class NPSResultsView(TemplateView):
    template_name = 'metrics/nps_results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['metric'] = NPSMetric.objects.filter(is_active=True).first()
        return context
