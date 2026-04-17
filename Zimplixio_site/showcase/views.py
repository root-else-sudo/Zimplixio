from django.conf import settings
from django.views.generic import ListView, DetailView
from .models import ShowcaseProject


class ShowcaseGalleryView(ListView):
    model = ShowcaseProject
    template_name = 'showcase/gallery.html'
    context_object_name = 'projects'

    def get_queryset(self):
        qs = ShowcaseProject.objects.filter(is_published=True).prefetch_related('tech_tags')
        industry = self.request.GET.get('industry')
        if industry and industry in dict(ShowcaseProject.INDUSTRY_CHOICES):
            qs = qs.filter(industry=industry)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['industry_choices'] = ShowcaseProject.INDUSTRY_CHOICES
        context['current_industry'] = self.request.GET.get('industry', '')
        return context


class ShowcaseDetailView(DetailView):
    model = ShowcaseProject
    template_name = 'showcase/detail-base.html'
    context_object_name = 'project'

    def get_queryset(self):
        return ShowcaseProject.objects.filter(is_published=True).prefetch_related('tech_tags', 'screenshots')

    def get_template_names(self):
        slug_map = {
            'ai-adoption-framework': 'showcase/detail-framework.html',
            'e-commerce':            'showcase/detail.html',
            'simple-forecast':       'showcase/detail-simple-forecast.html',
        }
        return [slug_map.get(self.object.slug, self.template_name)]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object.slug == 'ai-adoption-framework':
            context['api_available'] = bool(getattr(settings, 'ANTHROPIC_API_KEY', ''))
        return context
