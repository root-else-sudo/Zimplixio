import html
import logging
import re

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)

_DROPPED_BLOCKS = re.compile(r'(?is)<(style|script|head)\b.*?</\1>')
_LINE_BREAKS = re.compile(r'(?i)<br\s*/?>')
_BLOCK_ENDS = re.compile(r'(?i)</(p|div|tr|h[1-6]|table)>')


def render_plaintext(html_body):
    """Readable plain-text alternative for an HTML email.

    ``strip_tags`` alone is not enough: it keeps the contents of <style>,
    leaves HTML entities encoded, and drops <br> without putting a newline
    in its place, which runs paragraphs together.
    """
    body = _DROPPED_BLOCKS.sub('', html_body)
    body = _LINE_BREAKS.sub('\n', body)
    body = _BLOCK_ENDS.sub('\n', body)
    text = html.unescape(strip_tags(body))

    lines = []
    for line in (raw.strip() for raw in text.splitlines()):
        if line:
            lines.append(line)
        elif lines and lines[-1]:
            lines.append('')
    return '\n'.join(lines).strip()


class ContactEmailService:

    @staticmethod
    def send_visitor_received(submission):
        try:
            html_body = render_to_string(
                'emails/contact_visitor_received.html',
                {'submission': submission},
            )
            send_mail(
                subject="We've received your message — Zimplixio",
                message=render_plaintext(html_body),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[submission.email],
                html_message=html_body,
                fail_silently=False,
            )
        except Exception:
            logger.exception(
                'Failed to send contact acknowledgement to %s', submission.email
            )
