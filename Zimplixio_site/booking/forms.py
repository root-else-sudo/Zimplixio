from django import forms

from core.antispam import AntiSpamFormMixin
from core.antispam import make_form_token as _make_token
from core.antispam import read_form_token as _read_token

from .models import BookingRequest

# Unique per form, so a token minted for the contact form cannot be replayed
# against the booking form.
_TOKEN_SALT = 'booking.call.dwell'

_FIELD_CLASSES = (
    'w-full px-4 py-3 border border-gray-300 rounded-lg '
    'focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500'
)


def make_form_token(issued_at=None):
    """Signed proof of when the booking form was rendered."""
    return _make_token(_TOKEN_SALT, issued_at)


def read_form_token(token):
    """Seconds since the booking form was rendered, or None if missing/forged."""
    return _read_token(_TOKEN_SALT, token)


class BookingForm(AntiSpamFormMixin):
    """Booking form, gated by the shared decoy + dwell-token signals.

    The dwell floor is especially safe here: the wizard is three steps (pick a
    day, pick a time, fill the form), so a genuine visitor is never close to
    MIN_DWELL_SECONDS. See `core.antispam` for the refuse-versus-store rule.
    """

    TOKEN_SALT = _TOKEN_SALT
    LOG_LABEL = 'booking form'

    class Meta:
        model = BookingRequest
        fields = ['name', 'email', 'company', 'requested_date',
                  'requested_time', 'visitor_timezone', 'message']
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
            'requested_date': forms.HiddenInput(),
            'requested_time': forms.HiddenInput(),
            'visitor_timezone': forms.HiddenInput(),
            'message': forms.Textarea(attrs={
                'class': _FIELD_CLASSES,
                'placeholder': "Anything you'd like us to know before the call? (optional)",
                'rows': 4,
            }),
        }
