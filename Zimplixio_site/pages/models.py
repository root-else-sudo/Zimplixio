from django.db import models


class ContactSubmission(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    company = models.CharField(max_length=150, blank=True)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_spam = models.BooleanField(
        default=False,
        db_index=True,
        help_text='Set automatically by the contact form spam checks. '
                  'Flagged submissions are stored but never emailed.',
    )
    spam_reason = models.CharField(max_length=40, blank=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.name} — {self.submitted_at:%Y-%m-%d %H:%M}"
