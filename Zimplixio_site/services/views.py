from django.views.generic import TemplateView


class ServicesPageView(TemplateView):
    template_name = 'services/services.html'
