from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class NPSMetric(models.Model):
    score = models.IntegerField(
        validators=[MinValueValidator(-100), MaxValueValidator(100)],
        help_text="Net Promoter Score (-100 to 100)."
    )
    total_responses = models.PositiveIntegerField(default=0)
    last_updated = models.DateField()
    is_active = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'NPS Metric'
        verbose_name_plural = 'NPS Metrics'

    def __str__(self):
        return f"NPS {self.score} ({'Active' if self.is_active else 'Inactive'})"

    def save(self, *args, **kwargs):
        if self.is_active:
            NPSMetric.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)
