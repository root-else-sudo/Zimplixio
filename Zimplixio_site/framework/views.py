import json

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView
from django_ratelimit.decorators import ratelimit

from .content import STAGES
from .prompts import build_system_prompt, build_user_prompt


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
