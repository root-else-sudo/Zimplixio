import re

from django import forms

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


class SaveLeadForm(forms.Form):
    name = forms.CharField(max_length=200)
    email = forms.EmailField()

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        local, _, domain = email.rpartition('@')
        if domain in _BLOCKED_DOMAINS:
            raise forms.ValidationError('Please use a real business or personal email address.')
        if _SUSPICIOUS_PATTERN.match(local):
            raise forms.ValidationError(
                'Please enter your real name and email so we can follow up with you.'
            )
        return email
