import pathlib
import re
import time
from io import StringIO
from unittest.mock import patch

from django.conf import settings
from django.core import mail
from django.core.cache import cache
from django.core.management import call_command
from django.contrib.admin.sites import AdminSite
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from .admin import ContactSubmissionAdmin
from .forms import MIN_DWELL_SECONDS, make_form_token
from .models import ContactSubmission


class PageStatusTests(TestCase):
    def test_home_page(self):
        response = self.client.get(reverse('pages:home'))
        self.assertEqual(response.status_code, 200)

    def test_about_page(self):
        response = self.client.get(reverse('pages:about'))
        self.assertEqual(response.status_code, 200)

    def test_contact_page(self):
        response = self.client.get(reverse('pages:contact'))
        self.assertEqual(response.status_code, 200)

    def test_contact_success_page(self):
        response = self.client.get(reverse('pages:contact_success'))
        self.assertEqual(response.status_code, 200)

    def test_privacy_policy_page(self):
        response = self.client.get(reverse('pages:privacy_policy'))
        self.assertEqual(response.status_code, 200)

    def test_cookie_policy_page(self):
        response = self.client.get(reverse('pages:cookie_policy'))
        self.assertEqual(response.status_code, 200)


class ContactFormTests(TestCase):
    def test_contact_form_submit(self):
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'company': 'Test Co',
            'message': 'Hello, this is a test message.',
        }
        response = self.client.post(reverse('pages:contact'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ContactSubmission.objects.filter(email='test@example.com').exists())

    def test_contact_form_validation(self):
        data = {
            'name': '',
            'email': 'invalid',
            'message': '',
        }
        response = self.client.post(reverse('pages:contact'), data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(ContactSubmission.objects.exists())


class ContactConfirmationEmailTests(TestCase):
    @property
    def VALID(self):
        """A submission as a real browser sends it — decoy empty, token stamped.

        A property rather than a class attribute so every access gets a fresh
        token; a stale one would be rejected by the dwell-time check.
        """
        from pages.forms import make_form_token
        return {
            'name': 'Ada Lovelace',
            'email': 'ada@example.com',
            'company': 'Analytical Engines',
            'message': 'We need help forecasting demand.',
            'website': '',
            'ts': make_form_token(issued_at=time.time() - 30),
        }

    def setUp(self):
        # django-ratelimit counts in the default LocMemCache, which Django does
        # not reset between test methods — without this the 5/h cap leaks across
        # tests and later POSTs get a 429 instead of exercising the view.
        cache.clear()

    def test_confirmation_email_sent_to_visitor(self):
        self.client.post(reverse('pages:contact'), self.VALID)
        self.assertEqual(len(mail.outbox), 1)
        sent = mail.outbox[0]
        self.assertEqual(sent.to, ['ada@example.com'])
        self.assertEqual(sent.subject, "We've received your message — Zimplixio")
        self.assertEqual(sent.from_email, settings.DEFAULT_FROM_EMAIL)

    def test_confirmation_email_includes_their_name_and_message(self):
        self.client.post(reverse('pages:contact'), self.VALID)
        sent = mail.outbox[0]
        html = sent.alternatives[0][0]
        self.assertIn('Ada Lovelace', html)
        self.assertIn('We need help forecasting demand.', html)
        self.assertIn('Ada Lovelace', sent.body)

    def test_html_alternative_is_attached(self):
        self.client.post(reverse('pages:contact'), self.VALID)
        sent = mail.outbox[0]
        self.assertEqual(len(sent.alternatives), 1)
        self.assertEqual(sent.alternatives[0][1], 'text/html')

    def test_message_is_escaped_in_email(self):
        data = dict(self.VALID, message='<script>alert(1)</script>')
        self.client.post(reverse('pages:contact'), data)
        html = mail.outbox[0].alternatives[0][0]
        self.assertNotIn('<script>alert(1)</script>', html)
        self.assertIn('&lt;script&gt;', html)

    def test_no_email_when_submission_is_invalid(self):
        self.client.post(reverse('pages:contact'), {'name': '', 'email': 'bad', 'message': ''})
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(ContactSubmission.objects.count(), 0)

    def test_submission_survives_email_failure(self):
        with patch('pages.services.send_mail', side_effect=Exception('smtp down')):
            response = self.client.post(reverse('pages:contact'), self.VALID)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ContactSubmission.objects.count(), 1)

    def test_plaintext_fallback_is_clean(self):
        data = dict(self.VALID, message='First paragraph.\n\nSecond paragraph.')
        self.client.post(reverse('pages:contact'), data)
        body = mail.outbox[0].body
        self.assertNotIn('margin: 0', body, 'CSS leaked into the plain-text body')
        self.assertNotIn('font-family', body)
        self.assertNotIn('&mdash;', body, 'HTML entities left undecoded')
        self.assertNotIn('&#x27;', body)
        self.assertNotIn('&amp;', body)
        self.assertIn('First paragraph.', body)
        self.assertIn('Second paragraph.', body)
        self.assertNotIn('First paragraph.Second', body, 'line breaks were lost')


class ContactSpamFilterTests(TestCase):
    """Honeypot + dwell-time gating, and the email suppression that depends on it."""

    BASE = {
        'name': 'Ada Lovelace',
        'email': 'ada@example.com',
        'company': 'Analytical Engines',
        'message': 'We need help forecasting demand.',
    }

    def setUp(self):
        cache.clear()
        mail.outbox = []

    def payload(self, *, age_seconds=30, honeypot='', token=None, **overrides):
        """A submission as a real browser would send it."""
        from pages.forms import make_form_token
        data = dict(self.BASE)
        data['website'] = honeypot
        data['ts'] = token if token is not None else make_form_token(
            issued_at=time.time() - age_seconds
        )
        data.update(overrides)
        return data

    # ---------- a genuine submission still works ----------
    def test_human_submission_is_clean_and_emailed(self):
        r = self.client.post(reverse('pages:contact'), self.payload())
        self.assertEqual(r.status_code, 302)
        s = ContactSubmission.objects.get()
        self.assertFalse(s.is_spam)
        self.assertEqual(len(mail.outbox), 1)

    # ---------- honeypot ----------
    def test_honeypot_filled_is_flagged_and_not_emailed(self):
        r = self.client.post(reverse('pages:contact'),
                             self.payload(honeypot='http://spam.example'))
        self.assertEqual(r.status_code, 302, 'bot must still see the success redirect')
        s = ContactSubmission.objects.get()
        self.assertTrue(s.is_spam)
        self.assertEqual(len(mail.outbox), 0, 'no mail may leave for a flagged submission')

    # ---------- dwell time ----------
    def test_submitted_too_fast_is_refused_not_stored(self):
        """The one conclusive bot signal: refuse it, do not keep it.

        See ContactTooFastRejectionTests for the full behaviour.
        """
        self.client.post(reverse('pages:contact'), self.payload(age_seconds=0.5))
        self.assertFalse(ContactSubmission.objects.exists())
        self.assertEqual(len(mail.outbox), 0)

    def test_slow_genuine_submission_is_clean(self):
        self.client.post(reverse('pages:contact'), self.payload(age_seconds=1800))
        self.assertFalse(ContactSubmission.objects.get().is_spam)
        self.assertEqual(len(mail.outbox), 1)

    def test_stale_token_is_flagged(self):
        self.client.post(reverse('pages:contact'), self.payload(age_seconds=60 * 60 * 30))
        self.assertTrue(ContactSubmission.objects.get().is_spam)
        self.assertEqual(len(mail.outbox), 0)

    # ---------- tampering / direct POSTs ----------
    def test_missing_token_is_flagged(self):
        self.client.post(reverse('pages:contact'), self.payload(token=''))
        self.assertTrue(ContactSubmission.objects.get().is_spam)
        self.assertEqual(len(mail.outbox), 0)

    def test_forged_token_is_flagged(self):
        self.client.post(reverse('pages:contact'), self.payload(token='1763000000:forged'))
        self.assertTrue(ContactSubmission.objects.get().is_spam)
        self.assertEqual(len(mail.outbox), 0)

    def test_raw_post_with_no_spam_fields_at_all_is_flagged(self):
        """What every bot in the log actually does: POST the visible fields only."""
        self.client.post(reverse('pages:contact'), dict(self.BASE))
        self.assertTrue(ContactSubmission.objects.get().is_spam)
        self.assertEqual(len(mail.outbox), 0)

    # ---------- the decoy must be invisible and skipped by assistive tech ----------
    def test_honeypot_is_hidden_inline_not_via_stylesheet(self):
        html = self.client.get(reverse('pages:contact')).content.decode()
        self.assertIn('name="website"', html)
        row = [l for l in html.splitlines() if 'name="website"' in l][0]
        self.assertIn('display:none', row.replace(' ', ''),
                      'must be hidden by an inline style, not a CSS class')
        self.assertIn('tabindex="-1"', row)
        self.assertIn('autocomplete="off"', row)
        self.assertIn('aria-hidden="true"', row)

    def test_honeypot_has_no_visible_label(self):
        html = self.client.get(reverse('pages:contact')).content.decode()
        self.assertNotIn('>Website<', html)


class ContactTooFastRejectionTests(TestCase):
    """A sub-3-second POST is refused by the form, so it never becomes a row.

    Every other spam signal still flags-and-stores on purpose: the honeypot
    can be tripped by browser autofill, and a missing or stale dwell token
    can mean a tab left open overnight rather than a bot. Only the
    sub-3-second POST is conclusive enough to throw the submission away,
    and even then the visitor gets a form they can simply send again.
    """

    BASE = {
        'name': 'Ada Lovelace',
        'email': 'ada@example.com',
        'company': 'Analytical Engines',
        'message': 'We need help forecasting demand.',
    }

    def setUp(self):
        cache.clear()
        mail.outbox = []

    def payload(self, *, age_seconds=0.5, token=None):
        data = dict(self.BASE)
        data['website'] = ''
        data['ts'] = token if token is not None else make_form_token(
            issued_at=time.time() - age_seconds
        )
        return data

    def test_no_row_is_written(self):
        self.client.post(reverse('pages:contact'), self.payload())
        self.assertFalse(ContactSubmission.objects.exists())

    def test_no_email_is_sent(self):
        self.client.post(reverse('pages:contact'), self.payload())
        self.assertEqual(len(mail.outbox), 0)

    def test_the_form_is_redisplayed_rather_than_redirected(self):
        r = self.client.post(reverse('pages:contact'), self.payload())
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.context['form'].non_field_errors())

    def test_the_error_does_not_reveal_the_timing_rule(self):
        """A bot author reading the response must not learn what to tune."""
        r = self.client.post(reverse('pages:contact'), self.payload())
        error = ' '.join(r.context['form'].non_field_errors()).lower()
        for leak in ('second', 'fast', 'quick', 'speed', 'bot',
                     'spam', 'dwell', 'timer', 'wait'):
            self.assertNotIn(leak, error,
                             f'error text leaks the mechanism: {error!r}')

    def test_the_visitors_message_survives_the_rejection(self):
        """They must not have to retype what they wrote."""
        r = self.client.post(reverse('pages:contact'), self.payload())
        self.assertContains(r, 'We need help forecasting demand.')

    def test_the_rerendered_form_still_carries_the_original_token(self):
        """Why the retry below works: the bound form echoes the token back."""
        token = make_form_token(issued_at=time.time() - 0.5)
        r = self.client.post(reverse('pages:contact'), self.payload(token=token))
        self.assertContains(r, token)

    def test_a_rejected_visitor_can_resubmit_and_succeed(self):
        """The recovery path, and the reason refusing beats silently flagging.

        Today a false positive is stored as spam, never emailed, and the
        visitor is never told -- unrecoverable. Refused, they see an error
        and pressing Send again just works, because the token they send
        back is by then older than MIN_DWELL_SECONDS.
        """
        url = reverse('pages:contact')
        first = self.client.post(url, self.payload())
        self.assertEqual(first.status_code, 200)
        self.assertFalse(ContactSubmission.objects.exists())

        token = first.context['form']['ts'].value()
        later = time.time() + MIN_DWELL_SECONDS + 1
        with patch('pages.forms.time.time', return_value=later):
            second = self.client.post(url, self.payload(token=token))

        self.assertEqual(second.status_code, 302)
        self.assertFalse(ContactSubmission.objects.get().is_spam)
        self.assertEqual(len(mail.outbox), 1)

    # ---------- the other signals must NOT start rejecting ----------
    def test_honeypot_is_still_stored_for_review(self):
        self.client.post(reverse('pages:contact'),
                         dict(self.payload(age_seconds=30),
                              website='http://spam.example'))
        s = ContactSubmission.objects.get()
        self.assertTrue(s.is_spam)
        self.assertEqual(s.spam_reason, 'honeypot')

    def test_missing_token_is_still_stored_for_review(self):
        self.client.post(reverse('pages:contact'), self.payload(token=''))
        s = ContactSubmission.objects.get()
        self.assertTrue(s.is_spam)
        self.assertEqual(s.spam_reason, 'no_token')

    def test_stale_token_is_still_stored_for_review(self):
        self.client.post(reverse('pages:contact'),
                         self.payload(age_seconds=60 * 60 * 30))
        s = ContactSubmission.objects.get()
        self.assertTrue(s.is_spam)
        self.assertEqual(s.spam_reason, 'stale_token')


class SpamSignalPrecedenceTests(TestCase):
    """A refusable signal must win over a merely-flaggable one.

    _spam_reason() returns the FIRST signal it finds, so the order it checks
    them in decides whether a submission is refused or stored. The honeypot
    used to be checked first, which meant a bot that filled the decoy AND
    posted in under 3 seconds was stored rather than refused -- one line in
    the bot's script would have refilled the table.
    """

    BASE = {
        'name': 'Ada Lovelace',
        'email': 'ada@example.com',
        'company': 'Analytical Engines',
        'message': 'We need help forecasting demand.',
    }

    def setUp(self):
        cache.clear()
        mail.outbox = []

    def post(self, *, age_seconds, honeypot=''):
        data = dict(self.BASE)
        data['website'] = honeypot
        data['ts'] = make_form_token(issued_at=time.time() - age_seconds)
        return self.client.post(reverse('pages:contact'), data)

    def test_honeypot_and_fast_is_refused_not_stored(self):
        """The dwell floor is conclusive; tripping the decoy too cannot weaken it."""
        r = self.post(age_seconds=0.5, honeypot='http://spam.example')
        self.assertEqual(r.status_code, 200)
        self.assertFalse(ContactSubmission.objects.exists())
        self.assertEqual(len(mail.outbox), 0)

    def test_honeypot_at_human_speed_is_still_stored_for_review(self):
        """Autofill can trip the decoy, so a slow one stays recoverable."""
        r = self.post(age_seconds=30, honeypot='http://spam.example')
        self.assertEqual(r.status_code, 302)
        s = ContactSubmission.objects.get()
        self.assertTrue(s.is_spam)
        self.assertEqual(s.spam_reason, 'honeypot')
        self.assertEqual(len(mail.outbox), 0)


class SpamLoggingTests(TestCase):
    """The log is the only record of submissions that never become rows.

    clean() runs even when field validation has already failed, so a flagged
    submission with an invalid field is logged and then silently discarded.
    The log must not imply a row that does not exist.
    """

    BASE = {
        'name': 'Ada Lovelace',
        'email': 'ada@example.com',
        'company': 'Analytical Engines',
        'message': 'We need help forecasting demand.',
    }

    def setUp(self):
        cache.clear()

    def post(self, **over):
        data = dict(self.BASE)
        data['website'] = 'http://spam.example'
        data['ts'] = make_form_token(issued_at=time.time() - 30)
        data.update(over)
        return self.client.post(reverse('pages:contact'), data)

    def test_a_stored_flag_is_logged_as_flagged(self):
        with self.assertLogs('pages.forms', level='INFO') as log:
            self.post()
        self.assertEqual(ContactSubmission.objects.count(), 1)
        self.assertTrue(any('flagged as spam (honeypot)' in m for m in log.output),
                        log.output)

    def test_a_discarded_flag_says_so_and_names_the_invalid_field(self):
        with self.assertLogs('pages.forms', level='INFO') as log:
            self.post(email='not-an-email')
        self.assertFalse(ContactSubmission.objects.exists())
        joined = ' '.join(log.output)
        self.assertIn('discarded', joined,
                      'a discarded submission must not be logged as merely flagged')
        self.assertIn('email', joined, 'the log should name the field that failed')
        self.assertNotIn('flagged as spam', joined)


class TemplateCommentTests(TestCase):
    """Django's ``{# #}`` comment is single-line ONLY.

    The lexer's tag regex does not match across newlines, so a multi-line
    ``{# ... #}`` is not a comment at all: the braces are emitted as literal
    text and any ``{% %}`` tags between them are executed normally. This
    shipped to production once (contact.html, visible under the message
    field) and sat latent in _nps_badge.html, where it would have fired the
    moment an NPS score existed. Use ``{% comment %}...{% endcomment %}``
    for anything spanning more than one line.
    """

    TEMPLATES = pathlib.Path(__file__).resolve().parent.parent / 'templates'

    def test_no_template_opens_a_comment_it_does_not_close_on_the_same_line(self):
        offenders = []
        for path in sorted(self.TEMPLATES.rglob('*.html')):
            text = path.read_text()
            for match in re.finditer(r'\{#', text):
                close = text.find('#}', match.start())
                body = text[match.start() + 2:close] if close != -1 else text[match.start():]
                # Unclosed, spanning lines, or nesting a marker -- the lexer's
                # non-greedy {#.*?#} closes at the FIRST #}, so a nested one
                # silently spills the remainder of the line onto the page.
                if close == -1 or '\n' in body or '{#' in body or '#}' in body:
                    line = text[:match.start()].count('\n') + 1
                    offenders.append('%s:%d' % (path.relative_to(self.TEMPLATES), line))
        self.assertEqual(
            offenders, [],
            'multi-line {# #} is not a comment -- use {% comment %}: ' + ', '.join(offenders)
        )

    def test_contact_page_renders_no_literal_comment_markers(self):
        html = self.client.get(reverse('pages:contact')).content.decode()
        self.assertNotIn('{#', html)
        self.assertNotIn('#}', html)

    def test_nps_badge_stays_hidden_once_a_score_exists(self):
        """The partial is deliberately disabled; a score must not reveal it."""
        from django.template.loader import render_to_string
        out = render_to_string('partials/_nps_badge.html', {'nps_score': 72})
        self.assertNotIn('{#', out)
        self.assertNotIn('#}', out)
        self.assertNotIn('NPS Score', out,
                         'the badge is meant to stay hidden until results are ready')


class DesignSystemRuleTests(TestCase):
    """CLAUDE.md's UI rules, enforced instead of merely documented.

    Each of these has actually been violated in this repo. A rule in a
    document is advisory and costs context every session; a rule here fails
    the build and names the file and line.
    """

    TEMPLATES = pathlib.Path(__file__).resolve().parent.parent / 'templates'

    def _templates(self):
        return sorted(self.TEMPLATES.rglob('*.html'))

    def test_detail_base_has_no_per_project_conditionals(self):
        """detail-base.html is the shared skeleton; projects override blocks.

        A ``{% if project.slug == ... %}`` here is how that skeleton rots into
        a pile of special cases. Add ``detail-<slug>.html`` extending the base
        and override the block instead -- see CLAUDE.md.
        """
        path = self.TEMPLATES / 'showcase' / 'detail-base.html'
        offenders = [
            '%s:%d' % (path.name, i)
            for i, line in enumerate(path.read_text().splitlines(), 1)
            if re.search(r'\{%\s*if\b[^%]*\bslug\b', line)
        ]
        self.assertEqual(
            offenders, [],
            'override a block instead of branching on slug: ' + ', '.join(offenders))

    def test_no_ambient_blur_discs_inside_an_animated_hero(self):
        """``bg-white rounded-full blur-3xl`` shows as grey discs on the dark gradient.

        Scoped to the <section> carrying .hero-animated-bg, tracking nesting
        depth: the lighter static ``bg-gradient-to-br`` bands (privacy and
        cookie policy, the framework #assessment-cta) legitimately use one at
        ~10% opacity and must not trip this.
        """
        offenders = []
        for path in self._templates():
            lines = path.read_text().splitlines()
            for i, line in enumerate(lines):
                if 'hero-animated-bg' not in line:
                    continue
                depth = 0
                for j in range(i, len(lines)):
                    depth += lines[j].count('<section')
                    depth -= lines[j].count('</section>')
                    if 'blur-3xl' in lines[j] and 'rounded-full' in lines[j]:
                        offenders.append(
                            '%s:%d' % (path.relative_to(self.TEMPLATES), j + 1))
                    if depth <= 0:
                        break
        self.assertEqual(
            offenders, [],
            'ambient blur discs inside .hero-animated-bg: ' + ', '.join(offenders))

    def test_no_dark_mode_variants_in_markup(self):
        """The site is light-only, so a ``dark:`` utility is dead code.

        base.html keeps Tailwind's ``darkMode: 'class'`` deliberately, to stop
        stray variants activating from the OS preference. Comments may discuss
        ``dark:``; markup may not use it.
        """
        offenders = []
        for path in self._templates():
            for i, raw in enumerate(path.read_text().splitlines(), 1):
                # Strip comments, but not the // inside a https:// URL.
                line = re.sub(r'(?<!:)//.*$', '', raw)
                line = re.sub(r'\{#.*?#\}', '', line)
                if 'dark:' in line:
                    offenders.append('%s:%d' % (path.relative_to(self.TEMPLATES), i))
        self.assertEqual(
            offenders, [],
            'site is light-only, a dark: variant can never activate: '
            + ', '.join(offenders))


class ContactAdminActionTests(TestCase):
    """Bulk actions — the admin had none, so clearing 2k rows meant one at a time."""

    def setUp(self):
        self.admin = ContactSubmissionAdmin(ContactSubmission, AdminSite())
        self.request = RequestFactory().get('/')
        self.request.user = None
        # message_user needs a message store
        setattr(self.request, 'session', {})
        setattr(self.request, '_messages', FallbackStorage(self.request))
        for i in range(3):
            ContactSubmission.objects.create(
                name=f'n{i}', email=f'u{i}@example.com', message='m')

    def test_submissions_cannot_be_added_through_admin(self):
        self.assertFalse(self.admin.has_add_permission(self.request))

    def test_mark_as_read_updates_every_selected_row(self):
        self.admin.mark_as_read(self.request, ContactSubmission.objects.all())
        self.assertEqual(ContactSubmission.objects.filter(is_read=True).count(), 3)

    def test_mark_as_unread_reverses_it(self):
        ContactSubmission.objects.update(is_read=True)
        self.admin.mark_as_unread(self.request, ContactSubmission.objects.all())
        self.assertEqual(ContactSubmission.objects.filter(is_read=False).count(), 3)

    def test_mark_as_spam_sets_flag_and_reason(self):
        self.admin.mark_as_spam(self.request, ContactSubmission.objects.all())
        self.assertEqual(ContactSubmission.objects.filter(
            is_spam=True, spam_reason='manual').count(), 3)

    def test_mark_as_not_spam_clears_flag_and_reason(self):
        ContactSubmission.objects.update(is_spam=True, spam_reason='honeypot')
        self.admin.mark_as_not_spam(self.request, ContactSubmission.objects.all())
        self.assertEqual(ContactSubmission.objects.filter(
            is_spam=False, spam_reason='').count(), 3)

    def test_spam_can_be_filtered_in_the_changelist(self):
        self.assertIn('is_spam', self.admin.list_filter)
        self.assertIn('is_spam', self.admin.list_display)


class FlagContactSpamCommandTests(TestCase):
    """One-off backfill that classifies the submissions already in the table."""

    def setUp(self):
        self.google = ContactSubmission.objects.create(
            name='Robertfus', email='a@gmail.com', company='google',
            message='Hi, I wanted to know your price.')
        self.gibberish = ContactSubmission.objects.create(
            name='empvgigkuw', email='real.person@comcast.net', company='inoyxzttod',
            message='eklnixktjnwjwsuuyhyfxhvgqxjudk')
        self.legit = ContactSubmission.objects.create(
            name='Maria Fernandez', email='maria@brightpath.com',
            company='BrightPath Logistics', message='Our dispatch scheduling is a mess.')

    def _run(self, *args):
        out = StringIO()
        call_command('flag_contact_spam', *args, stdout=out)
        return out.getvalue()

    def test_dry_run_is_the_default_and_writes_nothing(self):
        output = self._run()
        self.assertEqual(ContactSubmission.objects.filter(is_spam=True).count(), 0)
        self.assertIn('dry run', output.lower())

    def test_apply_flags_the_google_campaign(self):
        self._run('--apply')
        self.google.refresh_from_db()
        self.assertTrue(self.google.is_spam)
        self.assertEqual(self.google.spam_reason, 'company_google')

    def test_apply_flags_the_gibberish_bot(self):
        self._run('--apply')
        self.gibberish.refresh_from_db()
        self.assertTrue(self.gibberish.is_spam)
        self.assertEqual(self.gibberish.spam_reason, 'gibberish')

    def test_a_real_submission_is_left_alone(self):
        self._run('--apply')
        self.legit.refresh_from_db()
        self.assertFalse(self.legit.is_spam)
        self.assertEqual(self.legit.spam_reason, '')

    def test_rerunning_is_idempotent(self):
        self._run('--apply')
        before = list(ContactSubmission.objects.values_list('id', 'is_spam', 'spam_reason'))
        self._run('--apply')
        self.assertEqual(
            list(ContactSubmission.objects.values_list('id', 'is_spam', 'spam_reason')),
            before)

    def test_already_flagged_rows_are_not_reclassified(self):
        self.legit.is_spam = True
        self.legit.spam_reason = 'manual'
        self.legit.save()
        self._run('--apply')
        self.legit.refresh_from_db()
        self.assertEqual(self.legit.spam_reason, 'manual')
