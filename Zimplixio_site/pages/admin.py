from django.contrib import admin
from .models import ContactSubmission


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'company', 'submitted_at', 'is_read']
    list_filter = ['is_read', 'submitted_at']
    readonly_fields = ['name', 'email', 'company', 'message', 'submitted_at']
    search_fields = ['name', 'email', 'company']

    def has_add_permission(self, request):
        return False
