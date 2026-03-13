from django.db import models


class AssessmentLead(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    readiness_level = models.CharField(max_length=50, blank=True)
    answers = models.JSONField(default=dict)

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Assessment Lead'
        verbose_name_plural = 'Assessment Leads'

    def __str__(self):
        return f'{self.name} <{self.email}> — {self.submitted_at:%Y-%m-%d}'
