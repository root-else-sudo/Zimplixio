from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, CreateView
from django_ratelimit.decorators import ratelimit

from showcase.models import ShowcaseProject
from .forms import ContactForm
from .services import ContactEmailService


class HomePageView(TemplateView):
    template_name = 'pages/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_projects'] = ShowcaseProject.objects.published()[:10]
        return context


class AboutPageView(TemplateView):
    template_name = 'pages/about.html'


class ServicesPageView(TemplateView):
    template_name = 'services/services.html'


class ContactView(CreateView):
    template_name = 'pages/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('pages:contact_success')

    @method_decorator(ratelimit(key='ip', rate='5/h', method='POST', block=False))
    def post(self, request, *args, **kwargs):
        if getattr(request, 'limited', False):
            return HttpResponse('Too many submissions. Please try again later.', status=429)
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        # Flagged submissions are stored for review but never acknowledged by
        # email — bot-supplied addresses belong to people who never wrote in,
        # and mailing them damages the sending domain's reputation.
        if not self.object.is_spam:
            ContactEmailService.send_visitor_received(self.object)
        return response


class ContactSuccessView(TemplateView):
    template_name = 'pages/contact_success.html'


class PrivacyPolicyView(TemplateView):
    template_name = 'pages/privacy_policy.html'


class CookiePolicyView(TemplateView):
    template_name = 'pages/cookie_policy.html'
