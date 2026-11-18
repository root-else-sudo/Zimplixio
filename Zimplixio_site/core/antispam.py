"""Shared anti-spam signals for public forms.

Two signals, deliberately treated **asymmetrically**:

- A sub-``MIN_DWELL_SECONDS`` POST is *refused* — no row is written at all.
  No human completes a form that fast, and a refused visitor can simply press
  Send again, because the re-rendered bound form echoes the original token
  back and it has by then aged past the floor.
- Everything else is *flagged* — the row is stored with ``is_spam=True`` and
  never emailed. Browser autofill can trip the decoy, and a missing or
  day-old token can mean a tab left open overnight, so those stay recoverable.

The ORDER the signals are checked in is load-bearing: only the first match is
returned, and that decides refuse-versus-store, so conclusive signals are
checked first. See ``docs/GOTCHAS.md``.

Extracted from ``pages.forms`` when the booking form needed the same
protection. Both forms are public, both mail the address they are handed,
and an unprotected one of those is what got the sending mailbox restricted by
Microsoft in November 2026.
"""

import logging
import time

from django import forms
from django.core import signing
from django.core.exceptions import ImproperlyConfigured

# A real person needs at least a few seconds to read a form and type into it.
# Bots POST the moment they parse the page.
MIN_DWELL_SECONDS = 3
# Beyond this the token is stale — a tab left open for a day, or a replayed capture.
MAX_DWELL_SECONDS = 60 * 60 * 24

# Shown when a submission is refused outright. Deliberately says nothing about
# why: a bot author reading the response must not learn which signal to tune.
REJECTION_MESSAGE = (
    'We could not process that submission. '
    'Please try sending your message again.'
)

# Signals conclusive enough to throw the submission away rather than store it.
REFUSED_REASONS = frozenset({'too_fast'})

# Hidden with an inline style rather than a CSS class on purpose: static assets
# carry no content hash here, Cloudflare serves main.css with max-age=14400 and
# Safari caches it in memory indefinitely, so a visitor on a stale stylesheet
# would SEE the decoy and fill it in. Inline styles ship with the (uncached) HTML.
HONEYPOT_STYLE = (
    'position:absolute !important; left:-10000px !important; '
    'width:1px !important; height:1px !important; overflow:hidden !important; '
    'display:none !important;'
)


def make_form_token(salt, issued_at=None):
    """Signed proof of when this form was rendered."""
    stamp = int(issued_at if issued_at is not None else time.time())
    return signing.Signer(salt=salt).sign(str(stamp))


def read_form_token(salt, token):
    """Seconds since the form was rendered, or None if missing/forged."""
    if not token:
        return None
    try:
        issued = int(signing.Signer(salt=salt).unsign(token))
    except (signing.BadSignature, ValueError):
        return None
    return time.time() - issued


class AntiSpamFormMixin(forms.ModelForm):
    """Adds a decoy field and a signed render timestamp to a ModelForm.

    The model must have ``is_spam`` (BooleanField) and ``spam_reason``
    (CharField). Subclasses set ``TOKEN_SALT`` to something unique so a token
    minted for one form cannot be replayed against another.

    Template authors: render ``{{ form.website }}{{ form.ts }}`` bare, outside
    the normal field loop, and skip ``form.SPAM_FIELDS`` inside it.
    """

    SPAM_FIELDS = ('website', 'ts')
    TOKEN_SALT = None

    # The decoy. Named to look like something worth filling in.
    website = forms.CharField(
        required=False,
        label='',
        widget=forms.TextInput(attrs={
            'style': HONEYPOT_STYLE,
            'tabindex': '-1',
            'autocomplete': 'off',
            'aria-hidden': 'true',
        }),
    )
    ts = forms.CharField(required=False, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.TOKEN_SALT:
            raise ImproperlyConfigured(
                '%s must set TOKEN_SALT' % type(self).__name__)
        # Stamp every freshly rendered (unbound) form.
        if not self.is_bound:
            self.fields['ts'].initial = make_form_token(self.TOKEN_SALT)

    def spam_reason(self):
        """Why this submission looks automated, or '' if it looks human.

        Order matters — see the module docstring. Conclusive signals first.
        """
        elapsed = read_form_token(self.TOKEN_SALT, self.data.get('ts'))

        # Conclusive: no human completes a form in under three seconds.
        if elapsed is not None and elapsed < MIN_DWELL_SECONDS:
            return 'too_fast'

        # Recoverable: autofill can fill the decoy, and a missing or day-old
        # token can mean a tab left open rather than a bot.
        if self.cleaned_data.get('website'):
            return 'honeypot'
        if elapsed is None:
            return 'no_token'
        if elapsed > MAX_DWELL_SECONDS:
            return 'stale_token'
        return ''

    def clean(self):
        cleaned = super().clean()
        reason = self.spam_reason()
        if not reason:
            return cleaned

        if reason in REFUSED_REASONS:
            # No row is created: form_valid() never runs.
            self._logger().info('%s refused (%s)', self._log_label(), reason)
            raise forms.ValidationError(REJECTION_MESSAGE, code=reason)

        # `is_spam`/`spam_reason` are not form fields, so construct_instance()
        # in _post_clean() leaves them alone.
        self.instance.is_spam = True
        self.instance.spam_reason = reason
        if self._errors:
            # clean() runs even after field validation has already failed, so
            # this submission never reaches form_valid() and never becomes a
            # row. Logged distinctly: refused and discarded submissions leave
            # nothing behind, so the log must not imply a row that is not there.
            self._logger().info('%s discarded (%s; invalid: %s)',
                                self._log_label(), reason, ','.join(sorted(self._errors)))
        else:
            self._logger().info('%s flagged as spam (%s)', self._log_label(), reason)
        return cleaned

    def _logger(self):
        """The concrete form's own module logger, not core's.

        Keeps log lines attributable to the app they came from, and keeps
        existing assertLogs('pages.forms') assertions working.
        """
        return logging.getLogger(type(self).__module__)

    def _log_label(self):
        return getattr(self, 'LOG_LABEL', type(self).__name__)
