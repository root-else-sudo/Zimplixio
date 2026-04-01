from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, CreateView
from django_ratelimit.decorators import ratelimit
from .forms import ContactForm


class HomePageView(TemplateView):
    template_name = 'pages/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from showcase.models import ShowcaseProject
        context['featured_projects'] = (
            ShowcaseProject.objects
            .filter(is_published=True)
            .prefetch_related('tech_tags')[:10]
        )
        return context


class AboutPageView(TemplateView):
    template_name = 'pages/about.html'


class ContactView(CreateView):
    template_name = 'pages/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('pages:contact_success')

    @method_decorator(ratelimit(key='ip', rate='5/h', method='POST', block=False))
    def post(self, request, *args, **kwargs):
        if getattr(request, 'limited', False):
            return HttpResponse('Too many submissions. Please try again later.', status=429)
        return super().post(request, *args, **kwargs)


class ContactSuccessView(TemplateView):
    template_name = 'pages/contact_success.html'


class PrivacyPolicyView(TemplateView):
    template_name = 'pages/privacy_policy.html'


class CookiePolicyView(TemplateView):
    template_name = 'pages/cookie_policy.html'
