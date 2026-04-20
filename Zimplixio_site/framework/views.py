import json
import logging

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit

from .forms import SaveLeadForm
from .models import AssessmentLead
from .prompts import build_system_prompt, build_user_prompt
from .services import LeadNotificationService
from .utils import parse_claude_json

logger = logging.getLogger(__name__)

REQUIRED_ANSWER_KEYS = {
    'industry', 'size', 'ai_usage', 'data_readiness',
    'leadership', 'goals', 'concerns', 'timeline',
}


@ratelimit(key='ip', rate='10/h', method='POST', block=False)
@require_POST
def save_lead_view(request):
    """Saves name + email after the assessment report has been generated."""
    if getattr(request, 'limited', False):
        return JsonResponse({'success': False, 'error': 'Rate limit exceeded.'}, status=429)

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid request body.'}, status=400)

    form = SaveLeadForm(data={'name': body.get('name', ''), 'email': body.get('email', '')})
    if not form.is_valid():
        first_error = next(iter(form.errors.values()))[0]
        return JsonResponse({'success': False, 'error': first_error}, status=400)

    name = form.cleaned_data['name']
    email = form.cleaned_data['email']
    readiness_level = body.get('readiness_level', '')
    answers = body.get('answers', {})

    AssessmentLead.objects.create(
        name=name,
        email=email,
        readiness_level=readiness_level,
        answers=answers,
    )
    LeadNotificationService.send(name, email, readiness_level, answers)

    return JsonResponse({'success': True})


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
        return JsonResponse({'success': False, 'error': 'Invalid request body.'}, status=400)

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
        result = parse_claude_json(message.content[0].text)
        return JsonResponse({'success': True, 'report': result})

    except json.JSONDecodeError:
        return JsonResponse(
            {'success': False, 'error': 'The AI returned an invalid response. Please try again.'},
            status=500,
        )
    except Exception:
        logger.exception('Unexpected error in assessment_view')
        return JsonResponse(
            {'success': False, 'error': 'An unexpected error occurred. Please try again.'},
            status=500,
        )
