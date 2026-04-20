import logging

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


class LeadNotificationService:

    @staticmethod
    def send(name, email, readiness_level, answers):
        recipient = getattr(settings, 'LEAD_NOTIFICATION_EMAIL', '')
        if not recipient:
            return
        try:
            admin_url = reverse('admin:framework_assessmentlead_changelist')
            context = {
                'name': name,
                'email': email,
                'readiness_level': readiness_level,
                'answers': answers,
                'admin_url': admin_url,
            }
            html = render_to_string('emails/framework_lead_notification.html', context)
            send_mail(
                subject=f'New AI Assessment Lead: {name}',
                message=strip_tags(html),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                html_message=html,
                fail_silently=False,
            )
        except Exception:
            logger.exception('Failed to send lead notification email')
