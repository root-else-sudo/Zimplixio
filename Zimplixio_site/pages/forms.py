from django import forms

from core.antispam import (
    MAX_DWELL_SECONDS,
    MIN_DWELL_SECONDS,
    REJECTION_MESSAGE,
    AntiSpamFormMixin,
)
from core.antispam import make_form_token as _make_token
from core.antispam import read_form_token as _read_token

from .models import ContactSubmission

# Unique per form, so a token minted for the contact form cannot be replayed
# against the booking form.
_TOKEN_SALT = 'pages.contact.dwell'

__all__ = [
    'ContactForm', 'make_form_token', 'read_form_token',
    'MIN_DWELL_SECONDS', 'MAX_DWELL_SECONDS', 'REJECTION_MESSAGE',
]


def make_form_token(issued_at=None):
    """Signed proof of when the contact form was rendered."""
    return _make_token(_TOKEN_SALT, issued_at)


def read_form_token(token):
    """Seconds since the contact form was rendered, or None if missing/forged."""
    return _read_token(_TOKEN_SALT, token)


_FIELD_CLASSES = (
    'w-full px-4 py-3 border border-gray-300 rounded-lg '
    'focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500'
)


class ContactForm(AntiSpamFormMixin):
    """Contact form, gated by the shared decoy + dwell-token signals.

    The behaviour — refuse a sub-3-second POST, flag everything else, never
    email a flagged submission — lives in `core.antispam`. See that module and
    `docs/GOTCHAS.md` for why the two signals are treated differently.
    """

    TOKEN_SALT = _TOKEN_SALT
    LOG_LABEL = 'contact form'

    class Meta:
        model = ContactSubmission
        fields = ['name', 'email', 'company', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': _FIELD_CLASSES,
                'placeholder': 'Your full name',
            }),
            'email': forms.EmailInput(attrs={
                'class': _FIELD_CLASSES,
                'placeholder': 'you@company.com',
            }),
            'company': forms.TextInput(attrs={
                'class': _FIELD_CLASSES,
                'placeholder': 'Company name (optional)',
            }),
            'message': forms.Textarea(attrs={
                'class': _FIELD_CLASSES,
                'placeholder': "Tell us what you're trying to solve.",
                'rows': 5,
            }),
        }
