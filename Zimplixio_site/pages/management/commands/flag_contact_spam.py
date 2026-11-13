"""Classify ContactSubmission rows that predate the form's spam checks.

The honeypot and dwell-time checks only apply to submissions made after they
were deployed. This backfills a verdict onto everything already in the table so
the admin changelist becomes usable, without deleting anything.

Dry run by default — pass --apply to write.
"""
import re

from django.core.management.base import BaseCommand
from django.db.models import Q

from pages.models import ContactSubmission

# Every row of the Nov 2026 campaign carried this hardcoded company value.
_CAMPAIGN_COMPANY = 'google'
# A second bot fills every field with random lowercase strings but uses real,
# scraped addresses — so the email is no help and the other fields are.
_GIBBERISH = re.compile(r'^[a-z]{8,12}$')


def classify(submission):
    """Return a spam_reason for an obviously automated submission, else ''."""
    if (submission.company or '').strip().lower() == _CAMPAIGN_COMPANY:
        return 'company_google'
    if (_GIBBERISH.match((submission.name or '').strip())
            and _GIBBERISH.match((submission.company or '').strip())):
        return 'gibberish'
    return ''


class Command(BaseCommand):
    help = 'Flag pre-existing spam contact submissions (dry run unless --apply).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--apply', action='store_true',
            help='Actually write the flags. Without this the command only reports.',
        )

    def handle(self, *args, **options):
        apply_changes = options['apply']
        # Never reclassify a row someone has already judged.
        candidates = ContactSubmission.objects.filter(
            Q(is_spam=False) & Q(spam_reason='')
        )

        buckets = {}
        to_update = []
        for s in candidates.iterator():
            reason = classify(s)
            if not reason:
                continue
            buckets[reason] = buckets.get(reason, 0) + 1
            s.is_spam = True
            s.spam_reason = reason
            to_update.append(s)

        total = ContactSubmission.objects.count()
        self.stdout.write(f'rows in table          : {total}')
        self.stdout.write(f'unjudged candidates    : {candidates.count()}')
        for reason, n in sorted(buckets.items(), key=lambda kv: -kv[1]):
            self.stdout.write(f'  would flag {reason:<16}: {n}')
        self.stdout.write(f'total to flag          : {len(to_update)}')

        if not apply_changes:
            self.stdout.write(self.style.WARNING(
                'dry run — nothing written. Re-run with --apply to commit.'))
            return

        ContactSubmission.objects.bulk_update(
            to_update, ['is_spam', 'spam_reason'], batch_size=500)
        self.stdout.write(self.style.SUCCESS(f'flagged {len(to_update)} submission(s).'))
