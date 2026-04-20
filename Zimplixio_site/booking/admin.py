from django.contrib import admin

from .models import BookingRequest, TimeSlot


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['day_of_week', 'start_time', 'end_time', 'is_active']
    list_filter = ['day_of_week', 'is_active']


@admin.register(BookingRequest)
class BookingRequestAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'requested_date', 'requested_time', 'status', 'created_at']
    list_filter = ['status', 'requested_date']
    list_editable = ['status']
    search_fields = ['name', 'email', 'company']

    def save_model(self, request, obj, form, change):
        if change and obj.pk:
            try:
                old_status = BookingRequest.objects.get(pk=obj.pk).status
            except BookingRequest.DoesNotExist:
                old_status = None
            if old_status != 'confirmed' and obj.status == 'confirmed':
                obj.confirm()
                return
        super().save_model(request, obj, form, change)
