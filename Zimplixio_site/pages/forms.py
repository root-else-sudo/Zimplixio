import logging
import time

from django import forms
from django.core import signing

from .models import ContactSubmission

logger = logging.getLogger(__name__)

# A real person needs at least a few seconds to read the form and type into it.
# Bots POST the moment they parse the page.
MIN_DWELL_SECONDS = 3
# Beyond this the token is stale — a tab left open for a day, or a replayed capture.
MAX_DWELL_SECONDS = 60 * 60 * 24

_TOKEN_SALT = 'pages.contact.dwell'

# Hidden with an inline style rather than a CSS class on purpose: static assets
# carry no content hash here, Cloudflare serves main.css with max-age=14400 and
# Safari caches it in memory indefinitely, so a visitor on a stale stylesheet
# would SEE the decoy and fill it in. Inline styles ship with the (uncached) HTML.
_HONEYPOT_STYLE = (
    'position:absolute !important; left:-10000px !important; '
    'width:1px !important; height:1px !important; overflow:hidden !important; '
    'display:none !important;'
)


def make_form_token(issued_at=None):
    """Signed proof of when this form was rendered."""
    stamp = int(issued_at if issued_at is not None else time.time())
    return signing.Signer(salt=_TOKEN_SALT).sign(str(stamp))


def read_form_token(token):
    """Seconds since the form was rendered, or None if missing/forged."""
    if not token:
        return None
    try:
        issued = int(signing.Signer(salt=_TOKEN_SALT).unsign(token))
    except (signing.BadSignature, ValueError):
        return None
    return time.time() - issued


_FIELD_CLASSES = (
    'w-full px-4 py-3 border border-gray-300 rounded-lg '
    'focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500'
)


class ContactForm(forms.ModelForm):
    # Fields that must never be rendered by the template's normal field loop.
    SPAM_FIELDS = ('website', 'ts')

    # The decoy. Named to look like something worth filling in.
    website = forms.CharField(
        required=False,
        label='',
        widget=forms.TextInput(attrs={
            'style': _HONEYPOT_STYLE,
            'tabindex': '-1',
            'autocomplete': 'off',
            'aria-hidden': 'true',
        }),
    )
    ts = forms.CharField(required=False, widget=forms.HiddenInput())

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Stamp every freshly rendered (unbound) form.
        if not self.is_bound:
            self.fields['ts'].initial = make_form_token()

    def _spam_reason(self):
        """Why this submission looks automated, or '' if it looks human.

        Deliberately does not raise: a flagged submission is still saved so a
        false positive is recoverable, it is just never emailed.
        """
        if self.cleaned_data.get('website'):
            return 'honeypot'

        elapsed = read_form_token(self.data.get('ts'))
        if elapsed is None:
            return 'no_token'
        if elapsed < MIN_DWELL_SECONDS:
            return 'too_fast'
        if elapsed > MAX_DWELL_SECONDS:
            return 'stale_token'
        return ''

    def clean(self):
        cleaned = super().clean()
        reason = self._spam_reason()
        if reason:
            # `is_spam`/`spam_reason` are not form fields, so construct_instance()
            # in _post_clean() leaves them alone.
            self.instance.is_spam = True
            self.instance.spam_reason = reason
            logger.info('contact form flagged as spam (%s)', reason)
        return cleaned
