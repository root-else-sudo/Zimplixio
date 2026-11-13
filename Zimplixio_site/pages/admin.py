from django.contrib import admin, messages

from .models import ContactSubmission


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'company', 'submitted_at', 'is_read', 'is_spam',
                    'spam_reason']
    list_filter = ['is_spam', 'is_read', 'submitted_at']
    readonly_fields = ['name', 'email', 'company', 'message', 'submitted_at',
                       'spam_reason']
    search_fields = ['name', 'email', 'company']
    actions = ['mark_as_read', 'mark_as_unread', 'mark_as_spam', 'mark_as_not_spam',
               'delete_selected']

    def has_add_permission(self, request):
        return False

    def get_changeform_initial_data(self, request):
        return {}

    @admin.action(description='Mark selected as read')
    def mark_as_read(self, request, queryset):
        n = queryset.update(is_read=True)
        self.message_user(request, f'{n} submission(s) marked as read.', messages.SUCCESS)

    @admin.action(description='Mark selected as unread')
    def mark_as_unread(self, request, queryset):
        n = queryset.update(is_read=False)
        self.message_user(request, f'{n} submission(s) marked as unread.', messages.SUCCESS)

    @admin.action(description='Mark selected as spam (no email is ever sent)')
    def mark_as_spam(self, request, queryset):
        n = queryset.update(is_spam=True, spam_reason='manual')
        self.message_user(request, f'{n} submission(s) marked as spam.', messages.SUCCESS)

    @admin.action(description='Mark selected as NOT spam')
    def mark_as_not_spam(self, request, queryset):
        n = queryset.update(is_spam=False, spam_reason='')
        self.message_user(request, f'{n} submission(s) cleared.', messages.SUCCESS)
