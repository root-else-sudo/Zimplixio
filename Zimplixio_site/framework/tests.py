import json
from unittest.mock import patch, MagicMock  # noqa: patch.dict used below

from django.test import TestCase, override_settings
from django.urls import reverse

from .prompts import build_system_prompt, build_user_prompt


@override_settings(RATELIMIT_ENABLE=False)
class AssessmentAPITests(TestCase):
    def setUp(self):
        self.url = reverse('framework:assessment')
        self.valid_answers = {
            'industry': 'Technology',
            'size': '11–50 employees',
            'current_usage': 'Experimenting informally',
            'value_target': 'Internal / Engineering productivity',
            'workflow_docs': 'Partially documented',
            'ai_literacy': 'Mixed — varies by role',
            'concerns': ['Cost overruns & runaway spend', 'Data security & IP exposure'],
            'goal_90_days': 'Launch a focused pilot',
        }

    def test_get_returns_405(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_post_missing_answers_returns_400(self):
        response = self.client.post(
            self.url,
            data=json.dumps({'answers': {'industry': 'Technology'}}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data['success'])

    def test_post_invalid_json_returns_400(self):
        response = self.client.post(
            self.url,
            data='not json',
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)

    @override_settings(ANTHROPIC_API_KEY='')
    def test_post_without_api_key_returns_503(self):
        response = self.client.post(
            self.url,
            data=json.dumps({'answers': self.valid_answers}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 503)
        data = response.json()
        self.assertFalse(data['success'])

    @override_settings(ANTHROPIC_API_KEY='test-key')
    def test_post_with_valid_answers_returns_report(self):
        mock_report = {
            'readiness_level': 'Developing',
            'readiness_summary': 'Your organization is experimenting but lacks governance.',
            'priority_stage': {
                'name': 'Guardians: Governance & Cost Control',
                'reason': 'Without governance, informal experiments risk becoming costly.'
            },
            'top_risks': [
                {'risk': 'Token cost overruns', 'detail': 'Unmonitored experimentation can escalate costs.'},
                {'risk': 'IP exposure', 'detail': 'Ungoverned usage risks sending proprietary data to LLMs.'},
                {'risk': 'Shadow AI', 'detail': 'Teams may adopt tools without IT visibility.'},
            ],
            'first_30_days': [
                'Audit current AI tool usage across all teams.',
                'Map your top 3 engineering workflows by time spent.',
                'Define a token budget for pilot projects.',
                'Establish a review process for AI-generated code.',
            ],
            'one_line_verdict': 'Formalize governance before scaling any AI initiative.',
        }

        mock_message = MagicMock()
        mock_message.content = [MagicMock(text=json.dumps(mock_report))]
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_message

        mock_anthropic = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client

        with patch.dict('sys.modules', {'anthropic': mock_anthropic}):
            response = self.client.post(
                self.url,
                data=json.dumps({'answers': self.valid_answers}),
                content_type='application/json',
            )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['report']['readiness_level'], 'Developing')
        self.assertEqual(len(data['report']['top_risks']), 3)

    @override_settings(ANTHROPIC_API_KEY='test-key')
    def test_post_malformed_response_returns_500(self):
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text='This is not JSON')]
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_message

        mock_anthropic = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client

        with patch.dict('sys.modules', {'anthropic': mock_anthropic}):
            response = self.client.post(
                self.url,
                data=json.dumps({'answers': self.valid_answers}),
                content_type='application/json',
            )
        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertFalse(data['success'])


class PromptTests(TestCase):
    def test_system_prompt_contains_stages(self):
        prompt = build_system_prompt()
        self.assertIn('STAGE 0', prompt)
        self.assertIn('STAGE 1', prompt)
        self.assertIn('STAGE 2', prompt)
        self.assertIn('STAGE 3', prompt)
        self.assertIn('People & Change Management', prompt)
        self.assertIn('Measurement & ROI', prompt)
        self.assertIn('JSON', prompt)

    def test_user_prompt_interpolates_answers(self):
        answers = {
            'industry': 'Healthcare',
            'size': '51–200 employees',
            'current_usage': 'One tool in production',
            'value_target': 'Both equally',
            'workflow_docs': 'Well documented',
            'ai_literacy': 'Moderate — comfortable with basic tools',
            'concerns': ['Regulatory & compliance risk', 'Data security & IP exposure'],
            'goal_90_days': 'Scale something already working',
        }
        prompt = build_user_prompt(answers)
        self.assertIn('Healthcare', prompt)
        self.assertIn('51–200 employees', prompt)
        self.assertIn('One tool in production', prompt)
        self.assertIn('Scale something already working', prompt)
        self.assertIn('Regulatory & compliance risk', prompt)

    def test_user_prompt_handles_missing_keys(self):
        prompt = build_user_prompt({})
        self.assertIn('Not specified', prompt)


class ShowcaseIntegrationTests(TestCase):
    def test_gallery_contains_framework_card(self):
        response = self.client.get(reverse('showcase:gallery'))
        self.assertContains(response, 'AI Adoption Framework')

    def test_detail_page_returns_200(self):
        response = self.client.get(reverse('showcase:detail', kwargs={'slug': 'ai-adoption-framework'}))
        self.assertEqual(response.status_code, 200)

    def test_detail_page_contains_framework_content(self):
        response = self.client.get(reverse('showcase:detail', kwargs={'slug': 'ai-adoption-framework'}))
        self.assertContains(response, 'id="framework-root"')
        self.assertContains(response, 'dist/framework-accordion.js')
        self.assertContains(response, 'Start Assessment')

    def test_detail_page_no_view_live_demo_link(self):
        response = self.client.get(reverse('showcase:detail', kwargs={'slug': 'ai-adoption-framework'}))
        self.assertNotContains(response, 'View Live Demo')
