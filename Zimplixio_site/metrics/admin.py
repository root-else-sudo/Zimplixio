from django.contrib import admin
from .models import NPSMetric


@admin.register(NPSMetric)
class NPSMetricAdmin(admin.ModelAdmin):
    list_display = ['score', 'total_responses', 'last_updated', 'is_active']
    list_filter = ['is_active']
