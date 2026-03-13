import json
import logging
import re

from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView
from django_ratelimit.decorators import ratelimit

logger = logging.getLogger(__name__)

from .content import STAGES
from .models import AssessmentLead
from .prompts import build_system_prompt, build_user_prompt

# Disposable / obviously fake email domains to reject
_BLOCKED_DOMAINS = {
    'test.com', 'example.com', 'fake.com', 'mailinator.com', 'guerrillamail.com',
    'throwaway.email', 'yopmail.com', 'sharklasers.com', 'guerrillamailblock.com',
    'grr.la', 'spam4.me', 'trashmail.com', 'trashmail.me', 'trashmail.io',
    'dispostable.com', 'maildrop.cc', 'tempr.email', 'tempmail.com', 'temp-mail.org',
    'getnada.com', 'burnermail.io',
}

_SUSPICIOUS_PATTERN = re.compile(
    r'^(test|fake|noreply|no-reply|admin|null|none|asdf|qwerty|aaa|bbb|xxx|user123)\b',
    re.IGNORECASE,
)


def _validate_lead_email(email: str) -> str | None:
    """Return an error string if the email is invalid or suspicious, else None."""
    email = email.strip().lower()
    if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
        return 'Please enter a valid email address.'
    local, _, domain = email.rpartition('@')
    if domain in _BLOCKED_DOMAINS:
        return 'Please use a real business or personal email address.'
    if _SUSPICIOUS_PATTERN.match(local):
        return 'Please enter your real name and email so we can follow up with you.'
    return None


@ratelimit(key='ip', rate='10/h', method='POST', block=False)
@require_POST
def save_lead_view(request):
    """Lightweight endpoint: saves name + email after the report has been generated."""
    if getattr(request, 'limited', False):
        return JsonResponse({'success': False, 'error': 'Rate limit exceeded.'}, status=429)

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid request body.'}, status=400)

    name = body.get('name', '').strip()
    email = body.get('email', '').strip()
    if not name:
        return JsonResponse({'success': False, 'error': 'Please enter your name.'}, status=400)
    email_error = _validate_lead_email(email)
    if email_error:
        return JsonResponse({'success': False, 'error': email_error}, status=400)

    readiness_level = body.get('readiness_level', '')
    answers = body.get('answers', {})

    AssessmentLead.objects.create(
        name=name,
        email=email,
        readiness_level=readiness_level,
        answers=answers,
    )

    _send_lead_notification(name, email, readiness_level, answers)

    return JsonResponse({'success': True})


def _send_lead_notification(name, email, readiness_level, answers):
    recipient = getattr(settings, 'LEAD_NOTIFICATION_EMAIL', '')
    if not recipient:
        return
    try:
        industry = answers.get('industry', '—')
        size = answers.get('size', '—')
        goal = answers.get('goal_90_days', '—')
        subject = f'New AI Assessment Lead: {name}'
        body = (
            f'A new lead completed the AI Readiness Assessment.\n\n'
            f'Name:             {name}\n'
            f'Email:            {email}\n'
            f'Readiness Level:  {readiness_level or "—"}\n\n'
            f'--- Quick Profile ---\n'
            f'Industry:         {industry}\n'
            f'Company size:     {size}\n'
            f'90-day goal:      {goal}\n\n'
            f'Log in to review full answers:\n'
            f'https://zimplixio.com/zm-admin/framework/assessmentlead/\n'
        )
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [recipient], fail_silently=False)
    except Exception:
        logger.exception('Failed to send lead notification email')


class FrameworkPageView(TemplateView):
    template_name = 'framework/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stages'] = STAGES
        context['api_available'] = bool(getattr(settings, 'ANTHROPIC_API_KEY', ''))
        return context


REQUIRED_ANSWER_KEYS = {
    'industry', 'size', 'current_usage', 'value_target',
    'workflow_docs', 'ai_literacy', 'concerns', 'goal_90_days',
}


@ratelimit(key='ip', rate='3/h', method='POST', block=False)
@require_POST
def assessment_view(request):
    if getattr(request, 'limited', False):
        return JsonResponse(
            {'success': False, 'error': 'Rate limit exceeded. Please try again later.'},
            status=429,
        )

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {'success': False, 'error': 'Invalid request body.'},
            status=400,
        )

    answers = body.get('answers', {})
    missing = REQUIRED_ANSWER_KEYS - set(answers.keys())
    if missing:
        return JsonResponse(
            {'success': False, 'error': f'Missing answers: {", ".join(sorted(missing))}'},
            status=400,
        )

    api_key = getattr(settings, 'ANTHROPIC_API_KEY', '')
    if not api_key:
        return JsonResponse(
            {'success': False, 'error': 'Assessment is temporarily unavailable.'},
            status=503,
        )

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model='claude-sonnet-4-6',
            max_tokens=1024,
            system=build_system_prompt(),
            messages=[{'role': 'user', 'content': build_user_prompt(answers)}],
        )

        raw = message.content[0].text
        # Strip any accidental markdown fences
        clean = raw.strip()
        if clean.startswith('```'):
            clean = clean.split('\n', 1)[1] if '\n' in clean else clean[3:]
        if clean.endswith('```'):
            clean = clean[:-3]
        clean = clean.strip()

        result = json.loads(clean)
        return JsonResponse({'success': True, 'report': result})

    except json.JSONDecodeError:
        return JsonResponse(
            {'success': False, 'error': 'The AI returned an invalid response. Please try again.'},
            status=500,
        )
    except Exception as e:
        return JsonResponse(
            {'success': False, 'error': 'An unexpected error occurred. Please try again.'},
            status=500,
        )
