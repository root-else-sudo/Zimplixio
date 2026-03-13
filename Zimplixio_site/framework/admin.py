from django.contrib import admin
from .models import AssessmentLead


@admin.register(AssessmentLead)
class AssessmentLeadAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'readiness_level', 'submitted_at')
    list_filter = ('readiness_level', 'submitted_at')
    search_fields = ('name', 'email')
    readonly_fields = ('submitted_at', 'answers')
    ordering = ('-submitted_at',)
